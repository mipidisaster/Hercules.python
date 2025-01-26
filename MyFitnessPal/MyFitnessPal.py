# This is effectively the top level of the MyFitnessPal script suite, where:
#   _MyFitnessPalApp_Controller.py  -> Functions to control and interpret the MyFitnessPal App (scroll, etc.)

from MyFitnessPal._MyFitnessPalApp_Controller import MyFitnessPalAppControl as phone_app
from MyFitnessPal._JSON import JSONCtrl as archieve
from MyFitnessPal.AppParameters import AppConfig as dv
from MyFitnessPal.FileLocations import LocalFileLocations as ls

from datetime import datetime, date, timedelta

import time
import os


# noinspection PyRedundantParentheses
class MyFitnessPal:
    def __init__(self, internal_appium_service = True):
        self.folder_root = ls.rootFolder  # Default the folder root to the specified location
        self.diary_calories = {}
        self.diary_contents = {}
        self.diary_macro    = {}

        self.app = phone_app(internal_appium_service)
        self.json = archieve(f"{os.path.join(self.folder_root, ".mem")}")

    def goto_diary_page(self):
        if (self.app.open() == 0):
            return 0
        time.sleep(2)

        if (self.app.open_diary_tab() == 0):  # Open the "Diary Tab" of today
            return 0
        time.sleep(2)

        time.sleep(10)

    def scrap_active_diary(self):
        self.diary_calories = {}
        self.diary_contents = {}
        self.diary_macro    = {}

        diary_date = self.app.read_diary_date()
        if (diary_date == 0):
            print("Diary entry not retried, skipping scrap...")
            return 0

        print(f"====={diary_date}=====")
        print(f"Retrieving the Diary entries for date {diary_date}...", end='')
        if (self.app.read_diary() == 0):
            print("Error encountered... exiting scrap...")
            print(f"=====END=====")
            return 0

        print("OK!")
        time.sleep(1)
        print(f"Retrieving Macros for date {diary_date}...", end='')
        if (self.app.read_diary_macros() == 0):
            print("Error encountered... exiting scrap...")
            print(f"=====END=====")
            return 0

        print("OK!")

        self.diary_calories['contents'] = self.app.calorie_tally
        self.diary_calories['date']     = str(diary_date.date())

        self.diary_contents['contents'] = self.app.diary_top_list
        self.diary_contents['date']     = str(diary_date.date())

        self.diary_macro['contents']    = self.app.diary_macro_list
        self.diary_macro['date']        = str(diary_date.date())

        print("Checking that the data is consistant...", end='')
        if (self.scrap_consistancy_check == 0):
            print("error...exiting")
            return 0
        print("OK")

        print("Saving to JSON file...", end='')
        self.json.append_DailySummary(self.diary_calories)
        self.json.append_Diary(self.diary_contents)
        self.json.append_Macro(self.diary_macro)

        self.json.write_datastore()
        print("OK")

        print(f"=====END=====")
        return 1

    def scrap_consistancy_check(self, expected_date):
        calories_burnt_diary = 0
        calories_burnt_macro = 0

        for i in self.diary_contents:
            calories_burnt_diary += i['contents']['calories']

        for i in self.diary_macro:
            calories_burnt_macro += i['contents']['calories']

        if (self.diary_calories['date'] == expected_date):
            first_check = True
        else:
            first_check = False

        if (self.diary_calories['contents']['calories'] == calories_burnt_diary):
            second_check = True
        else:
            second_check = False

        if (self.diary_calories['contents']['calories'] == calories_burnt_macro):
            third_check = True
        else:
            third_check = False

        if ((first_check is False) or (second_check is False) or (third_check is False)):
            print(f"Error with the scrap, data doesn't match -> Expected date {expected_date}, "
                  f"Date scrapped -> {self.diary_calories['date']}, "
                  f"Calories Tally = f{self.diary_calories['contents']['calories']}, "
                  f"Total from Diary = {calories_burnt_diary}, "
                  f"Total from Macro = {calories_burnt_macro}, ")
            return 0
        else:
            return 1

    def scrap_diary_from_date(self, start_date=datetime.now(), number_of_dates=1, step=-1):
        if not (isinstance(start_date, datetime) or isinstance(start_date, date)):
            print(f"Provided start date of {start_date}, is not recognised, exiting...")
            return 0

        if (number_of_dates == 0):
            print("Exiting, cannot scrap '0' days!")
            return 0

        first_pass = True

        for offset in range(number_of_dates):
            date_offset = timedelta(days=offset)
            target_date = start_date + date_offset
            if (first_pass is True or abs(step) > 7):
                self.app.open_diary_date(target_date)

            else:
                for j in range(0, abs(step)):
                    if (step < 0):
                        self.app.previous_day()
                    else:
                        self.app.next_day()

            time.sleep(2)
            try:
                if (self.scrap_active_diary() == 0):
                    print("Error in scrap...exiting...")

            except:
                print("Unknown error encountered, exiting...")
                return 0


            first_pass = False