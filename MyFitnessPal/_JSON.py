import json     # Import the json module

from MyFitnessPal.AppParameters import AppConfig as dv

# Useful links to understand the layout of the below class.
#https://www.w3schools.com/python/python_lists.asp
#https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/


class JSONCtrl:
    fileLocation = ""       # Variable to store the path to where the json file is to be stored
    curContents = {}        # Current contents of OxaLife that have been captured so far

    #=============================================================================================#
    def read_datastore(self):
        try:                                                # Attempt to read the json file
            temp = open(self.fileLocation, 'r')             # If able to read file
            self.curContents = json.load(temp)              # Capture the contents in class
            temp.close()                                    # close file

        except:                                             # if unable to read (as not there)
            self.curContents = {}                           # Define a dictionary
            self.curContents["app_sw_version"] = dv.app_sw_version
            self.curContents["DailySummary"] = []
            self.curContents["Diary"] = []
            self.curContents["Macro"] = []

            self.write_datastore()                          # Then export to data to file

    def write_datastore(self):                              # Export data to the json file, and override!
        temp = open(self.fileLocation, 'w')                 # Open file in write mode
        json.dump(self.curContents, temp, indent = 4)       # Dump JSON data, and make easy to read
        temp.close()                                        # Close file

    def __init__(self, fileLoc):                            # Constructor for "OxaLifeJSON"
        self.fileLocation = fileLoc
        self.read_datastore()

    @staticmethod
    def remove_duplicates_by_date(dict_list):
        seen_dates = set()
        unique_dicts = []

        for d in dict_list:
            if d['date'] not in seen_dates:
                seen_dates.add(d['date'])
                unique_dicts.append(d)

        return unique_dicts

    def __append_general(self, dictionary_name, newData):
        self.curContents[dictionary_name].insert(0, newData.copy())     # Force latest data to front

        self.curContents[dictionary_name] = JSONCtrl.remove_duplicates_by_date(
            sorted(self.curContents[dictionary_name], key=lambda x: (x["date"])))
        # This will first sort based upon the date, then remove any duplicates of entries with the same date
        # only accepting the first entry; which will be the new entry

    def append_DailySummary(self, newData):
        self.__append_general("DailySummary", newData)

    def append_Diary(self, newData):
        self.__append_general("Diary", newData)

    def append_Macro(self, newData):
        self.curContents["Macro"].append(newData.copy())
