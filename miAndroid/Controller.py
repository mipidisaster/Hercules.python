#!/usr/bin/env python
# This script covers basic interfacing and layout of the Android emulation.

# External imports/from statements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# -- libraries needed only in this class
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_service import AppiumService

from appium.webdriver.common.appiumby import AppiumBy

# support of waiting
from appium.webdriver.extensions.android.nativekey import AndroidKey
from bs4 import BeautifulSoup   # Used to parser the xml out from the WebElement

# -- libraries needed in children
from selenium.webdriver.support.ui import WebDriverWait  # Functions for waiting
from selenium.webdriver.support import expected_conditions as EC

# -- Import selenium error messages/exceptions
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

# Internal imports/from statements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from miAndroid.PhoneParameters import PhoneConfig as dv


# noinspection PyRedundantParentheses
class AndroidCtrl():
    def __init__(self, internal_appium_service=True):
        self.appium_service = None
        self.internal_appium_service = False    # Stores whether the class will have a active Appium Service internal

        if (internal_appium_service is True):
            self.start_appium_service()

        self.driver = webdriver.Remote(dv.appium_server_url,
                                       options=UiAutomator2Options().load_capabilities(dv.capabilities))

        self.phone_wait = WebDriverWait(self.driver, dv.phone_interaction_wait_time)
        self.am_active = 1
        self.background_view_active = 0     # Assumes that this function has been called whilst phone is NOT in the
                                            # background view

    def __del__(self):
        # Called at destruction of the class. Created to ensure that the phone emulation returns to a default setup,
        # for future scripts
        if (self.am_active == 1):
            self.quit()         # Close the driver
            print("Webdriver has been closed")

        print("I have been destroyed!")

    def quit(self):
        print("Closing down Android controller....")
        self.close_all_apps()   # Close every app present (will check if the background view is active and enable if
                                # not)
        self.driver.quit()      # Close the driver
        self.am_active = 0      # Capture that this "app" instance has been made in-active to ensure that when the
                                # "__del__" function is called, it won't attempt to go to background view/close stuff

        if (self.internal_appium_service is True):
            self.stop_appium_service()

    def start_appium_service(self):
        print("Starting the Appium Service/Server...", end='')
        self.appium_service = AppiumService()
        self.appium_service.start()
        print("OK")
        self.internal_appium_service = True

    def stop_appium_service(self):
        print("Closing the Appium Service/Server...", end='')
        self.appium_service.stop()
        self.internal_appium_service = False
        print("OK")

    def back(self):
        # Wrapper for the 'webdriver' back function
        self.driver.back()

    def export_current_xml(self, parser='lxml', file=None):
        parser_screen = BeautifulSoup(self.driver.page_source, features=parser).prettify()

        if (file is None):
            print(parser_screen)

        else:
            f = open(file, 'w')
            print(parser_screen, file=f)
            f.close()

    def android_backgroundapp_view(self):
        # Trigger the app background view (and confirm that this has been selected)
        self.background_view_active = 1     # background view has been triggered, update state
        self.driver.press_keycode(AndroidKey.APP_SWITCH)

    def android_background_view_is_empty(self):
        # Check if the background view has the "No recent items" text present
        try:
            self.phone_wait.until(EC.visibility_of_all_elements_located(
                ("xpath", "//*[@content-desc='No recent items']")))
            return 1

        except TimeoutException:
            print("There are still items in the background view")
            return 0

    def check_screen_is_homeview(self):
        # This function is to confirm that the current viewset is indeed the homeview, with nothing else visible.
        # This is done by confirming...
        # That there is a "resource-id"="com.google.android.apps.nexuslauncher:id/drag_layer", parameter. That within
        # this there is a "/workspace" parameter as well.
        try:
            # Check 1, see if
            drag_layer = self.phone_wait.until(EC.visibility_of_all_elements_located(
                ("xpath", "//*[contains(@resource-id, 'com.google.android.apps.nexuslauncher:id/drag_layer')]")))

            workspace = drag_layer[0].find_element(by=AppiumBy.XPATH,
                                                   value=".//*[contains(@resource-id, "
                                                         "'com.google.android.apps.nexuslauncher:id/workspace')]")

            # Will only get to this point if both of the above don't error. Therefore, this page is indeed the
            # "Homepage" so return 1
            self.background_view_active = 0  # As have confirmed that the homeview is active, update state
            return 1

        except TimeoutException or NoSuchElementException:
            print("Current page isn't the homepage")
            return 0

    def open_app_folder(self):
        # The structure of my Emulated Android phone, will be to have a folder at the "Home" level with the following
        # name "Auto App Folder". Within this will be ALL the apps that I intend or have automated
        try:
            folder_object = self.phone_wait.until(EC.element_to_be_clickable(("xpath", "//*[@text='Auto App Folder']")))
            # Look for and open the "Auto App Folder"
            if (folder_object.get_attribute("class") == "android.widget.TextView"):
                folder_object.click()

            # After having clicked, check that this has indeed opened a folder, with the same name + now the class has
            # changed to "EditText"
            folder_object = self.phone_wait.until(EC.element_to_be_clickable(("xpath", "//*[@text='Auto App Folder']")))
            if (folder_object.get_attribute("class") == "android.widget.EditText"):
                return 1
            else:
                return 0

        except TimeoutException:
            print("Attempt to open the Auto App Folder has resulted in an error...")
            return 0

    def close_all_apps(self):
        # This function will put the Phone into the "Home/background" view, and then close/shutdown the app that is at
        # the focus. This should be the latest app that was running prior to the "Home/background" being triggered
        if (self.background_view_active != 1):              # If the background view is NOT active, then
            self.android_backgroundapp_view()               # Trigger the background view

        # At this point, we are confident that the background view is active. Now to confirm that there is something
        # that needs to be closed...
        if (self.android_background_view_is_empty() == 1):  # If the background task as nothing to close
            self.android_backgroundapp_view()               # Trigger the background view again, to return to normal
            self.check_screen_is_homeview()                 # Then re-confirm homeview (and update class state
            return

        # Now....here, we are in the background view AND there is something that needs to be removed!
        apps_running = self.driver.find_elements("xpath", "//*[@content-desc]")
        # Whilst in the background view, there should only be two entries which have a 'content-desc'. Which is the top
        # level (with a ''), and the home button (with a 'Home').
        # So will loop, and swipe "up" the last but one entry...

        while (len(apps_running) > 2):
            to_close = apps_running[-2]  # Believe that this *should* give me the last but one
            try:
                print("Closing app", to_close.get_attribute("content-desc"))

            except NoSuchElementException or StaleElementReferenceException:
                print("Unable to determine name of app, but I'm closing it...")

            start_x = int(to_close.rect['x'] + (9 * to_close.rect['width'] / 10))
            end_x   = start_x

            start_y = int(to_close.rect['y'] + (9 * to_close.rect['height'] / 10))
            end_y   = to_close.rect['y']
            # self.driver.flick(863, 1073, 863, 209)
            self.driver.flick(start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y)
            # Parameters selected as the bounds for the background app view, is *assumed* to be the same -
            # [182,209][898,1936]
            # Selected halfway through all the above, and then drag up only in the "y" direction to 209...seemed to
            # work

            # Re-calculate the number of apps running
            if (self.check_screen_is_homeview() == 1):  # If detect that the homepage is active. Then all background
                                                        # tasks have been closed
                break
            else:
                apps_running = self.driver.find_elements("xpath", "//*[@content-desc]")
