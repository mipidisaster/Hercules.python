class AppConfig:
    app_sw_version              = "24.24.0"

    app_interaction_wait_time   = 15    # seconds

    # Dates (reference - https://strftime.org/):
    #-------------------------------------------
    calendar_xml_datestamp_format           = "%a, %b %#d"      # Expected format of the datestamp:'Sat, Jan 4'
    calendar_xml_datestamp_format_w_year    = "%a, %b %#d, %Y"  # Expected format of the datestamp:'Fri, Jan 3, 2025'
                                                                # on Linux change '#' to '-'
    diary_datestamp_format          = "%A, %b %d, %Y"           # Expected format of the datestamp:'Saturday, Jan 4, 2025'
    # -------------------------------------------

    # MyFitnessPal "XPATH" parameters
    meal_name_header    = "com.myfitnesspal.android:id/sectionHeaderRelativeLayout"
    diary_entry         = "com.myfitnesspal.android:id/foodSearchViewFoodItem"