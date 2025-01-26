# This script covers the basic interfacing, and understanding of the MyFitnessPal app.

# External imports/from statements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# -- Needed to work the 'miAndroid' class/'Selenium/Appium' driver
from selenium.webdriver.support.ui import WebDriverWait  # Functions for waiting
from selenium.webdriver.support import expected_conditions as EC

# -- Import selenium error messages/exceptions
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
# TODO improve script by introducing the specific expections to the above selenium errors

from datetime import datetime, timedelta, date
import time

# Internal imports/from statements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from miAndroid.Controller import AndroidCtrl
from MyFitnessPal.AppParameters import AppConfig as dv


# noinspection PyRedundantParentheses
class MyFitnessPalAppControl(AndroidCtrl):

    def __init__(self, internal_appium_service=True):
        AndroidCtrl.__init__(self, internal_appium_service)
        self.clear_internal_memory_of_diary()

        self.app_wait = WebDriverWait(self.driver, dv.app_interaction_wait_time)

    # =================================================================================================================
    # CHECK VIEW/DATA
    # ---------------
    #   The following section covers functions which are used to determine if specific views/Data/elements are current
    #   and or in the expected format
    #   Majority of these are internal functions only
    #       "__check" - Internal function
    #       "check"
    #       "what_is_active_view"
    # =================================================================================================================
    def __check_interface_ribbon(self):
        # Basic interface check, to ensure that the MyFitnessPal app is still up and running
        try:
            mfp_window = self.driver.find_elements("xpath", "//*[@content-desc]")
            if (len(mfp_window) < 4):
                return 0

            if (mfp_window[-4].get_attribute('resource-id') == "com.myfitnesspal.android:id/action_dashboard" and
                    mfp_window[-3].get_attribute('resource-id') == "com.myfitnesspal.android:id/action_diary" and
                    mfp_window[-2].get_attribute('resource-id') == "com.myfitnesspal.android:id/action_plans" and
                    mfp_window[-1].get_attribute('resource-id') == "com.myfitnesspal.android:id/action_more"):
                return 1
            else:
                return 0

        except (NoSuchElementException, StaleElementReferenceException) as e:
            return 0

    def __interface_ribbon_location(self):
        try:
            ribbon = self.driver.find_element("xpath",
                                              ".//*[@resource-id='com.myfitnesspal.android:id/bottomContainer']")

            return ribbon.rect
        except NoSuchElementException:
            return 0

    def __check_view_is_home_tab(self, silent=False):
        # Verify that the MyFitnessPal app has indeed been opened. This is done by checking for know information on the
        # app main page
        # First check, ensure that the view is still within the MyFitnessPal interface
        if (self.__check_interface_ribbon() == 1):
            first_check = True
        else:
            first_check = False

        try:
            # Second check, ensure that the 'Today' entry is in current view
            current_view = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", "//*[@resource-id='layoutDashboardParentColumn']")))

            text_element = current_view.find_element("class name", "android.widget.TextView")

            if (text_element.get_attribute("text").split('\n') == ["Today"]):
                # Confirm that the only text in the selected element is 'Today'
                second_check = True
            else:
                second_check = False

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            second_check = False

        third_check = True
        # Third check present incase I can think of some third condition to improve robustness of the script

        if (first_check and second_check and third_check):
            return 1
        else:
            if (silent is False):
                print(f"Check to see if screen view is the 'MyFitnessPal Home Tab View' failed, check results - "
                      f"{first_check}, {second_check}, {third_check}")
            return 0

    def __check_view_is_diary(self, silent=False):
        # Verify that the MyFitnessPal app has indeed been opened. This is done by checking for know information on the
        # app main page
        # First check, ensure that the view is still within the MyFitnessPal interface
        if (self.__check_interface_ribbon() == 1):
            first_check = True
        else:
            first_check = False

        try:
            # Second check, ensure that within a tab view, there is text stating "Diary"
            current_view = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", "//*[@resource-id='com.myfitnesspal.android:id/toolbar_container']")))

            text_element = current_view.find_element("class name", "android.widget.TextView")

            if (text_element.get_attribute("text").split('\n') == ["Diary"]):
                # Confirm that the only text in the selected element is 'Diary'
                second_check = True
            else:
                second_check = False

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            second_check = False

        third_check = True
        # Third check present incase I can think of some third condition to improve robustness of the script

        if (first_check and second_check and third_check):
            return 1
        else:
            if (silent is False):
                print(f"Check to see if screen view is the 'MyFitnessPal Diary Tab View' failed, check results - "
                      f"{first_check}, {second_check}, {third_check}")
            return 0

    def __check_diary_calendar_selected_date(self):
        selected_date = self.driver.find_element(
            "xpath", "//*[@resource-id='com.myfitnesspal.android:id/mtrl_picker_header_selection_text']").text
        selected_date = datetime.strptime(selected_date, "%b %d, %Y").date()
        # Format - Jan 4, 2025
        return selected_date

    def __check_diary_calendar_pending_date(self):
        pending_date = self.driver.find_element(
            "xpath", "//*[@resource-id='com.myfitnesspal.android:id/month_navigation_fragment_toggle']").text
        pending_date = datetime.strptime(pending_date, "%B %Y").date()
        # Format - January 2025
        return pending_date

    def what_is_active_view(self, silent=True):
        if (self.__check_view_is_home_tab(silent=silent) == 1):
            print("The current view is the HOME TAB screen")
            return 1

        if (self.__check_view_is_diary(silent=silent) == 1):
            print("The current view is the DIARY TAB screen")
            return 1

        if (self.__check_interface_ribbon() == 0):
            print("The current view is not a recognised MyFitnessPal viewset")
            return 0

        # If reached this point, then unable to determine the view. Hence exit
        print("Unable to determine the viewset, however believe it is not a MyFitnessPal viewset")
        return 0

    @staticmethod
    def check_diary_entry(web_element):
        # Will check if the element (WebElement) that is provided is a valid diary entry
        # Currently valid elements, are:
        #   Headers
        #   Diary entries
        #   TODO include Fasting entries
        #   TODO include the water quantity (this should be covered already)

        recognised_resources = [
            dv.meal_name_header,
            dv.diary_entry
        ]

        # Find the immediate children to the element provided as input
        try:
            element_child = web_element.find_elements("xpath", ".//child::*")
            quick_list = [e.get_attribute('resource-id') for e in element_child]

        except NoSuchElementException:
            print("Error encountered when trying to read provided element...")
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst trying to read the provided element...")
            #TODO tidy the below, such that it is a function from the 'miAndroid' class, as could be useful
            print(web_element.get_attribute('outerHTML'))  # Get information on the web_element that may have errored

            return 0

        match_found = False
        for resource_to_check in recognised_resources:

            if (resource_to_check in quick_list):
                match_found = True
                break

        if match_found is True:
            return 1
        else:
            return 0

    # =================================================================================================================
    # NAVIGATION
    # ----------
    #   The following section covers functions which are used to navigate through the MyFitnessPal app
    #   Function naming typically starts with:
    #       "open"
    #       "find"
    #       "swipe"
    # =================================================================================================================
    def open(self):
        # Open up the OxaLife app, which is located within the Top Level Automated Folder
        try:
            self.open_app_folder()  # First open the top level folder (assumes that this hasn't been opened yet)
            self.app_wait.until(EC.element_to_be_clickable(("xpath", "//*[@text='MyFitnessPal']"))).click()
            # Look for and open the "Oxa Life" App
            time.sleep(3)
            # Prior to doing the check, give the app slightly longer to load than typically used. So do 3 checks,
            # spaced out by ~2s
            count = 3
            while (self.__check_interface_ribbon() != 1 or count == 0):
                time.sleep(2)
                count = count - 1

            # Confirm that the app has opened correctly.
            return self.__check_view_is_home_tab()

        except TimeoutException:
            print("Attempt to open the MyFitnessPal app has resulted in an error...")
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst attempting to open MyFitnessPal...")
            return 0

    def open_diary_tab(self):
        try:
            self.app_wait.until(EC.element_to_be_clickable(
                ("xpath", "//*[contains(@resource-id, 'com.myfitnesspal.android:id/action_diary')]"))).click()
            time.sleep(3)

            # Confirm that the app has opened correctly.
            return self.__check_view_is_diary()

        except TimeoutException:
            print("Unable to find/select the 'Diary' tab...")
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst trying to select the 'Diary' tab...")
            return 0

    def open_diary_date(self, requested_date):
        if isinstance(requested_date, date) and not isinstance(requested_date, datetime):
            # Do nothing if the parameter is of type datetime.date
            pass
        elif isinstance(requested_date, datetime):
            # Convert datetime to date if the parameter is of type datetime
            requested_date = requested_date.date()
        else:
            print(f"Provided start date of {requested_date}, is not recognised, exiting...")
            return 0

        todays_date = datetime.today()
        todays_date_text    = todays_date.strftime(dv.calendar_xml_datestamp_format)

        target_year         = requested_date.year
        target_month        = requested_date.month
        target_date_text    = requested_date.strftime(dv.calendar_xml_datestamp_format)
        target_date_w_year  = requested_date.strftime(dv.calendar_xml_datestamp_format_w_year)

        # First ensure that the current view is the diary:
        if (self.__check_view_is_diary(silent=True) != 1):
            print("Current view isn't the diary, so exiting...")
            return 0

        try:
            # Open up the diary calendar view:
            self.driver.find_element("xpath", "//*[@resource-id='com.myfitnesspal.android:id/date_bar']").click()

            # Confirm view
            self.app_wait.until(EC.visibility_of_all_elements_located(
                ("xpath", "//*[@resource-id='com.myfitnesspal.android:id/mtrl_calendar_selection_frame']")))
            # NOTE - the entry below this is 'com.myfitnesspal.android:id/mtrl_calendar_day_selector_frame'

            # Ready the current date selected, and convert into 'datetime' format, and check against intended date
            if (self.__check_diary_calendar_selected_date() == requested_date):
                print("Requested date is already in active view")
                self.driver.find_element("xpath",
                                         "//*[@resource-id='com.myfitnesspal.android:id/cancel_button']").click()
                return 1

            # As well as the "SELECTED DATE" (big text on top of window). There is also the 'pending date', which is
            # the date/year that is currently on view for the user to select, and until a new date has been selected the
            # "SELECTED DATE" will not be updated
            if (target_year != self.__check_diary_calendar_pending_date().year):
                # Open year view
                self.driver.find_element(
                    "xpath", "//*[@resource-id='com.myfitnesspal.android:id/month_navigation_fragment_toggle']").click()

                # Confirm view
                self.app_wait.until(EC.visibility_of_all_elements_located(
                    ("xpath", "//*[@resource-id='com.myfitnesspal.android:id/mtrl_calendar_year_selector_frame']")))

                # SOME LEVEL OF SCROLLING TO BE INTRODUCED
                # Confirm if the current view has the year of interest. So create a list of all the years on view, they
                # will appear in the xml view as 'Navigate to year <YEAR>'. With the current year saying
                # 'Navigate to current year <YEAR>'
                # Therefore search for 'Navigate to ' and ' year ' - should work...
                #   No need to capture the CURRENT year, as already determined that this is not what we want
                scroll_attempts = 10
                while (scroll_attempts != 0):
                    current_years_on_view = [int(x.get_attribute("content-desc").split(' ')[-1])
                                             for x
                                             in self.driver.find_elements(
                            "xpath",
                            "//*[contains(@content-desc, 'Navigate to ') and "
                            "contains(@content-desc, ' year ')]")]

                    if (target_year in current_years_on_view):
                        break

                    else:
                        # Determine whether to scroll up, for earlier years...
                        if (min(current_years_on_view) == todays_date.year):
                            min_year_text = f'Navigate to current year {min(current_years_on_view)}'
                        else:
                            min_year_text = f'Navigate to year {min(current_years_on_view)}'

                        # Determine whether to scroll down, for later years...
                        if (max(current_years_on_view) == todays_date.year):
                            max_year_text = f'Navigate to current year {max(current_years_on_view)}'
                        else:
                            max_year_text = f'Navigate to year {max(current_years_on_view)}'

                        min_web_element = self.driver.find_element("xpath", f"//*[@content-desc='{min_year_text}']")
                        max_web_element = self.driver.find_element("xpath", f"//*[@content-desc='{max_year_text}']")

                        if (target_year < min(current_years_on_view)):
                            self.driver.scroll(min_web_element, max_web_element, 5000)  # Take 5s
                        else:
                            self.driver.scroll(max_web_element, min_web_element, 5000)  # Take 5s

                        # Some level of infinite loop control
                        scroll_attempts = scroll_attempts - 1

                if (target_year == todays_date.year):
                    year_string = f'Navigate to current year {target_year}'
                else:
                    year_string = f'Navigate to year {target_year}'
                self.driver.find_element("xpath", f"//*[@content-desc='{year_string}']").click()

                # Confirm that the YEAR has been captured in 'pending date'
                if (target_year != self.__check_diary_calendar_pending_date().year):
                    print("Error encountered when attempting to select the YEAR. Please investigate code...")
                    return 0

            # CORRECT YEAR SHOULD NOW BE SELECTED

            if (target_month != self.__check_diary_calendar_pending_date().month):
                month_delta = target_month - self.__check_diary_calendar_pending_date().month
                # Negative numbers mean that need to go to previous months. Positive numbers mean that need to go to
                # next months

                if (month_delta < 0):
                    search_text = 'com.myfitnesspal.android:id/month_navigation_previous'
                else:
                    search_text = 'com.myfitnesspal.android:id/month_navigation_next'

                for months_to_skip in range(0, abs(month_delta)):
                    self.driver.find_element("xpath", f"//*[@resource-id='{search_text}']").click()
                    time.sleep(2)

                # Confirm that the MONTH has been captured in 'pending date'
                if (target_month != self.__check_diary_calendar_pending_date().month):
                    print("Error encountered when attempting to select the MONTH. Please investigate code...")
                    return 0

            # CORRECT YEAR/MONTH SHOULD NOW BE SELECTED
            # Things to attempt - adding year at end, or adding 'Today ' at start
            try:
                if (target_date_text == todays_date_text):
                    target_date_text = f"Today {target_date_text}"

                print(f"Searching for -> '{target_date_text}' ", end="")
                self.driver.find_element("xpath", f"//*[@content-desc='{target_date_text}']").click()
                print("Success!")

            except NoSuchElementException:
                print("Failure...attempting including year...")
                print(f"Searching for -> '{target_date_w_year}'")
                self.driver.find_element("xpath", f"//*[@content-desc='{target_date_w_year}']").click()

            # Confirm that the date has been selected
            if (self.__check_diary_calendar_selected_date() == requested_date):
                print(f"Requested {requested_date} date has been selected")
                self.driver.find_element("xpath",
                                         "//*[@resource-id='com.myfitnesspal.android:id/confirm_button']").click()
                return 1

            else:
                print("Error found when selecting the date of interest....investigate the code...")
                return 0

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print("Unable to determine if the calendar view has appeared, exiting...")
            return 0

    def previous_day(self):
        try:
            day_navigation = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", ".//*[@resource-id='com.myfitnesspal.android:id/btnPrevious']")))
            day_navigation.click()
            return 1


        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            return 0

    def next_day(self):
        try:
            day_navigation = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", ".//*[@resource-id='com.myfitnesspal.android:id/btnNext']")))
            day_navigation.click()
            return 1


        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            return 0

    def find_diary_entries(self):
        # Function will retrieve and return all WebElements which are determined to be valid diary entries
        try:
            # XPATH search for an element with resource-id = "com.myfitnesspal.android:id/diary_recycler_view", and
            # return ALL child under this WebElement (/child::*)
            diary_recycler = self.driver.find_elements("xpath",
                              "//*[@resource-id='com.myfitnesspal.android:id/diary_recycler_view']/child::*")

            return [entry for entry in diary_recycler if self.check_diary_entry(entry) == 1]

        except NoSuchElementException:
            print("Unable to find the 'Diary Recycler View' to retrieve the diary entries, exiting...")
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst trying to retrieve diary entries...")
            return 0

    def __find_visible_diary_entries(self):
        current_web_entries = self.find_diary_entries()  # Get all the current diary entries
        current_web_entries = [x for x in current_web_entries if (self.diary_webelement_obscured_level(x) == 0)]
        return (current_web_entries)

    # =================================================================================================================
    # READ DATA
    # ----------
    #   The following section covers functions which are able to read the current screen, and retrieve useful
    #   information from it.
    #   Function naming typically starts with:
    #       "read"
    # =================================================================================================================
    # =================================================================================================================
    # > Diary Top-Level Data
    #   ----------
    #       This sub-section includes functions to read the "Diary tab view".
    #

    internal_food_dairy_generic_template = {
        "type": "",  # 'Meal', 'Food', 'Water', 'Fasting'
        "name": "",
        "time": "",
        "calories": ""
    }
    external_food_diary_template = {
        "meal": "",
        "time": "",
        "name": "",
        "calories": ""
    }

    @staticmethod
    def read_diary_lite_single_entry(web_element):
        toplevel_diary_entry = MyFitnessPalAppControl.internal_food_dairy_generic_template.copy()

        # Function will return text string detailing the information that is visible for this element
        if (MyFitnessPalAppControl.check_diary_entry(web_element) == 0):
            print("WebElement provided is not a recognised 'MyFitnessPal' diary element")
            return 0

        try:
            # Of the web_element provided, retrieve the elements directly below this
            element_child = web_element.find_elements("xpath", ".//child::*")
            quick_list = [e.get_attribute('resource-id') for e in element_child]

        except NoSuchElementException:
            print("Error encountered when trying to read provided element...")
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst trying to read the provided element...")
            # TODO tidy the below, such that it is a function from the 'miAndroid' class, as could be useful
            print(web_element.get_attribute('outerHTML'))  # Get information on the web_element that may have errored
            return 0

        # Determine which type of WebElement has been provided...
        try:
            if dv.meal_name_header in quick_list:
                # If the element is a "Meal Header" than
                meal_name = web_element.find_element(
                    "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/txtSectionHeader']"
                ).text
                toplevel_diary_entry['type'] = 'Meal'
                toplevel_diary_entry['name'] = meal_name
                return toplevel_diary_entry

        except NoSuchElementException:
            print("Error encountered whilst attempting to retrieve the Meal Name...")
            # TODO tidy the below, such that it is a function from the 'miAndroid' class, as could be useful
            print(web_element.get_attribute('outerHTML'))   # Get information on the web_element that may have errored
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst trying to the Meal Name...")
            return 0

        textfound = "Unable to find any of 'Description', 'Details', 'Calories'"
        try:
            if dv.diary_entry in quick_list:
                # If the element is a "Diary Entry" than
                item_description = web_element.find_element(
                    "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/txtItemDescription']"
                ).text
                textfound = f"Found 'Description' - {item_description}"

                item_details = web_element.find_element(
                    "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/txtItemDetails']"
                ).text
                textfound = f"{textfound}Found 'Details' - {item_details}"

                item_calories = web_element.find_element(
                    "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/txtCalories']"
                ).text
                textfound = f"{textfound}Found 'Calories' - {item_calories}"
                # TODO, can I make use of EC.staleness_of()

                try:
                    entry_time = web_element.find_element(
                        "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/entry_timestamp']"
                    ).text
                    toplevel_diary_entry['type'] = 'Food'
                    toplevel_diary_entry['name'] = f"{item_description}, {item_details}"
                    toplevel_diary_entry['time'] = entry_time
                    toplevel_diary_entry['calories'] = item_calories
                    return toplevel_diary_entry

                except NoSuchElementException:
                    toplevel_diary_entry['type'] = 'Food'
                    toplevel_diary_entry['name'] = f"{item_description}, {item_details}"
                    toplevel_diary_entry['time'] = ""
                    toplevel_diary_entry['calories'] = item_calories

                return toplevel_diary_entry

        except NoSuchElementException:
            #TODO May get to this entry if there is a note written. Need to get the function to recognise this
            print(f"Error encountered whilst attempting to retrieve the Food Diary Entry. {textfound}")
            # TODO tidy the below, such that it is a function from the 'miAndroid' class, as could be useful
            print(web_element.get_attribute('outerHTML'))   # Get information on the web_element that may have errored
            return 0
        except StaleElementReferenceException:
            print("Encountered a stale WebElement error whilst trying to the Food Diary Entry...")
            return 0

        print("Unrecognised element provided, exiting...")
        return 0

    def diary_webelement_obscured_level(self, web_element):
        # Function will calculate how obscured the element is, relative to the interface ribbon
        # "0" being not obscured, and "100" being totally hidden
        ribbon_top = self.__interface_ribbon_location()
        if (ribbon_top == 0):
            ribbon = self.driver.find_element(
                "xpath", ".//*[@resource-id='android:id/navigationBarBackground']")

            ribbon = ribbon.rect
            ribbon['y'] += 0            # This part of the function isn't really needed, however included as part of
            ribbon_top = ribbon['y']    # troubleshooting
        else:
            ribbon_top = ribbon_top['y']
        element_top = web_element.rect['y']
        element_height = web_element.rect['height']

        if ((element_top + element_height) < ribbon_top):
            # If the bottom of the element is above the ribbon_top, then return "0"
            return_element = 0
        elif ((element_top + element_height) == ribbon_top):
            # To cater for an instance where the bottom is exactly at the top of the ribbon. Return a percentage of
            # obscurement.
            # As in the instances of
            return_element = 0.001
        else:
            if (element_top >= ribbon_top):
                # If the top of the element is below the ribbon_top, then return "100"
                return_element = 100
            else:
                # In this statement, there will be a level of overlap between the ribbon, and element. Return how much
                # is hidden
                return_element = ((element_top + element_height) - ribbon_top) / element_height
                return_element *= 100   # Scale into percentage

        return return_element

    def swipe_to_extreme_of_diary(self, direction="BOTTOM"):
        previous_web_entries = []

        if (direction == "BOTTOM"):
            strt = -1
            endd = 0
        else:
            strt = 0
            endd = -1

        for i in range(1, 64):  # Ensure that the loops are limited, 64 chosen arbitrarily
            current_web_entries = self.find_diary_entries()
            current_web_entries = [x for x in current_web_entries if (self.diary_webelement_obscured_level(x) == 0)]
            unique_index = AndroidCtrl.get_unique_index_of_webelement(current_web_entries, previous_web_entries,
                                                                      reverse=False)

            if (len(unique_index) == 0 or unique_index == []):
                break

            previous_web_entries += [current_web_entries[i] for i in unique_index]
            self.driver.scroll(current_web_entries[strt], current_web_entries[endd], 500 * len(current_web_entries))

        return 0

    # =================================================================================================================
    # > Individual food macro data
    #   ----------
    #       This sub-section includes the functions to read and store the macro data linked to food in the diary
    #
    macro_food_template = {
        "meal": "com.myfitnesspal.android:id/textMeal",
        "time": "com.myfitnesspal.android:id/textTimeValue",
        "name": "com.myfitnesspal.android:id/txtFoodName",
        "units": "com.myfitnesspal.android:id/txtServingSize",
        "servings": "com.myfitnesspal.android:id/txtNoOfServings",
        
        "calories": "com.myfitnesspal.android:id/txtCalories",
        "carbohydrates": "com.myfitnesspal.android:id/txtTotalCarbs",
        "fat": "com.myfitnesspal.android:id/txtTotalFat",
        "protein": "com.myfitnesspal.android:id/txtProtein",
        "vitamin a": "com.myfitnesspal.android:id/txtVitaminA",
        "cholesterol": "com.myfitnesspal.android:id/txtCholesterol",
        "saturated fat": "com.myfitnesspal.android:id/txtSaturated",
        "polyunsaturated fat": "com.myfitnesspal.android:id/txtPolyunsaturated",
        "monounsaturated fat": "com.myfitnesspal.android:id/txtMonosaturated",
        "trans fat": "com.myfitnesspal.android:id/txtTrans",
        "sodium": "com.myfitnesspal.android:id/txtSodium",
        "potassium": "com.myfitnesspal.android:id/txtPotassium",
        "fiber": "com.myfitnesspal.android:id/txtDietaryFiber",
        "sugar": "com.myfitnesspal.android:id/txtSugars",
        "vitamin c": "com.myfitnesspal.android:id/txtVitaminC",
        "calcium": "com.myfitnesspal.android:id/txtCalcium",
        "iron": "com.myfitnesspal.android:id/txtIron"
    }

    def read_macros(self):
        macros = MyFitnessPalAppControl.macro_food_template.copy()
        macro_count = len(macros)
        macros_read = [0] * macro_count

        first_pass = True
        # variables used to help manage the scrolling of the view
        top_element     = []
        bottom_element  = []

        for i in range(1, 8):   # Ensure that the loops are limited, 8 chosen arbitrarily (however as limited data in
                                # view, this is assumed to be enough)
            for index, macro in enumerate(macros):
                try:
                    if (macros_read[index] == 1):
                        continue

                    macro_txt = self.driver.find_element("xpath", f".//*[@resource-id='{macros[macro]}']")
                    if (self.diary_webelement_obscured_level(macro_txt) == 0):
                        # No need to do a check of the visibility of the entries, as this macro view doesn't appear to have
                        # the interface ribbon present.
                        macros_read[index] = 1
                        macros[macro] = macro_txt.text
                        macro_count -= 1
                        if (macro_count == 0):
                            break

                        if (first_pass is True):
                            top_element     = macro_txt
                            bottom_element  = macro_txt
                            first_pass      = False

                        if (macro_txt.rect['y'] < top_element.rect['y']):
                            top_element = macro_txt

                        if (macro_txt.rect['y'] > bottom_element.rect['y']):
                            bottom_element = macro_txt

                except NoSuchElementException:
                    # As are cycling through the WHOLE array, not all entries will be present. So it is expected that
                    # this exception will be used a few times
                    None

            if (top_element == [] or bottom_element == []):
                print("Not matches for macros in the first pass, exiting...")
                return 0

            if (macro_count == 0):
                break

            self.driver.scroll(bottom_element, top_element, 500)

        if (macro_count != 0):
            print("Unable to find some of the macros within the food entry")
            return 0

        return macros

    # =================================================================================================================
    # > Full Diary read
    #   ----------
    #       This sub-section includes the functions to read the full information within the diary. The amount of data
    #       retrieved is based upon the input into "read_diary"
    def clear_internal_memory_of_diary(self):
        self.calorie_tally = []
        self.diary_top_list = []
        self.diary_pre_macro_list = []
        self.diary_macro_list = []
        self.diary_current_time = "No Time"
        self.diary_current_meal = "Undefined"
        self.diary_entry_type = 'Undefined'

    def __update_internal_memory_of_diary(self, web_elements):
        entry = MyFitnessPalAppControl.read_diary_lite_single_entry(web_elements)
        if (entry != 0):
            self.diary_entry_type = entry['type']

            match entry['type']:
                case 'Meal':
                    self.diary_current_meal = entry['name']
                    self.diary_current_time = "No Time"

                case 'Food':
                    if (self.diary_current_meal != "Water" and self.diary_current_meal != "Exercise"):
                        self.diary_pre_macro_list.append(entry.copy())

                    if (entry['time'] != ''):
                        self.diary_current_time = entry['time']

                    food = self.external_food_diary_template.copy()
                    food['meal'] = self.diary_current_meal
                    food['time'] = self.diary_current_time
                    food['name'] = entry['name']
                    food['calories'] = entry['calories']

                    self.diary_top_list.append(food)

    def read_diary_date(self):
        self.swipe_to_extreme_of_diary("TOP")

        try:
            diary_date = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", "//*[@resource-id='com.myfitnesspal.android:id/btnDate']"))).text

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print("Unable to find the date of this diary entry...")
            return 0

        today_date = datetime.today()
        # Re-create so as to remove the specific time of the day
        today_date = datetime(year=today_date.year, month=today_date.month, day=today_date.day)
        # The Date of the will appear as one of the following:
        # Today, Yesterday, Tomorrow
        # Thursday 23 Jan   < of the current active year
        # Friday 12 Jul 2024

        if (diary_date == "Today"):
            return today_date

        elif (diary_date == "Yesterday"):
            return today_date - timedelta(days=1)

        elif (diary_date == "Tomorrow"):
            return today_date + timedelta(days=1)

        # At this point confirmed that the diary is not within 1 day of today's date.
        try:
            return datetime.strptime(diary_date, dv.diary_datestamp_format)

        except ValueError:
            return datetime.strptime(diary_date + f", {today_date.year}", dv.diary_datestamp_format)

    def read_daily_calories_tally(self):
        try:
            calorie_goal = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", "//*[@resource-id='com.myfitnesspal.android:id/goal']"))).text
            calorie_total = self.app_wait.until(EC.visibility_of_element_located(
                ("xpath", "//*[@resource-id='com.myfitnesspal.android:id/food']"))).text

            return_value = {
                "goal": calorie_goal,
                "calories": calorie_total
            }

            return return_value

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print("Unable to get the diary, daily calorie tallies, exiting...")
            return 0

    def read_diary(self):
        self.clear_internal_memory_of_diary()

        self.swipe_to_extreme_of_diary("TOP")
        scan_down_from = 0

        self.calorie_tally = self.read_daily_calories_tally()

        for i in range(1, 64):   # Ensure that the loops are limited, 64 chosen arbitrarily
            current_web_entries = self.__find_visible_diary_entries()
            if (current_web_entries == 0):
                print("Encountered an error with looking at the top level diary entries, exiting...")
                return 0

                # Filter out any entry which happens to be hidden by the Ribbon Interface, at bottom of screen
            diary_entries = [x for x in current_web_entries if (x.rect['y'] > scan_down_from)]
                # This "scan line" has been introduced, as unable to make use of entry matching to discard read entries.
                # Also cannot make use of the webelements themselves, as they are not always unique.
                # So, "scan line" will be updated to equal the 'y' entry of the element that is 'swiped' (later on)
                # Any element which is greater than this line will be included, below this discarded

            if (len(diary_entries) == 0 or diary_entries == []):    # If nothing to read, keep going till see the
                continue                                            # 'Diary Complete' button at the bottom

            [self.__update_internal_memory_of_diary(x) for x in diary_entries]

            try:
                complete_diary_button = self.driver.find_element(
                    "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/btnComplete']")
                if (self.diary_webelement_obscured_level(complete_diary_button) == 0):
                    break

            except NoSuchElementException:
                # Expect to be in this state at the start of the loop, so don't do anything
                None

            self.driver.scroll(current_web_entries[-1], current_web_entries[0], 500*len(current_web_entries))
            scan_down_from = current_web_entries[-1].rect['y']
            time.sleep(1)

        self.swipe_to_extreme_of_diary("TOP")

        return 1

    def read_diary_macros(self):
        self.swipe_to_extreme_of_diary("TOP")

        for macro_to_find in self.diary_pre_macro_list:

            for i in range(1, 64):   # Ensure that the loops are limited, 64 chosen arbitrarily
                current_web_entries = self.__find_visible_diary_entries()
                food_in_view = [MyFitnessPalAppControl.read_diary_lite_single_entry(x) for x in current_web_entries]
                if (current_web_entries == 0):
                    print("Encountered an error with looking at the top level diary entries, exiting...")
                    return 0

                try:
                    food_to_click = food_in_view.index(macro_to_find)

                    current_web_entries[food_to_click].click()
                    time.sleep(1)
                    self.diary_macro_list.append(self.read_macros())
                    time.sleep(1)
                    self.back()

                    break

                except ValueError:
                    None

                try:
                    complete_diary_button = self.driver.find_element(
                        "xpath", ".//*[@resource-id='com.myfitnesspal.android:id/btnComplete']")
                    if (self.diary_webelement_obscured_level(complete_diary_button) == 0):
                        break

                except NoSuchElementException:
                    # Expect to be in this state at the start of the loop, so don't do anything
                    None

                self.driver.scroll(current_web_entries[-1], current_web_entries[0], 500 * len(current_web_entries))
                time.sleep(1)

        if (len(self.diary_macro_list) != len(self.diary_pre_macro_list)):
            print("Unable to find all macros of originally read diary entries, exiting...")
            return 0

        self.swipe_to_extreme_of_diary("TOP")

        return 1