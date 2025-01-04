# miAndroid
This is to be a top level/parent package/class for the interfacing with a Android Phone Emulation. The class mainly covers basis setup of the 'Appium' Webdriver, as well as a few functions to check the emulation is in a fit state for the intended app to be opened.

# Class structure
The XML below gives a view of the class, as can be seen the class 'AndroidCtrl' is dependent upon the 'PhoneConfig'. The 'PhoneConfig' only contains variables which are to be used to change 'basic' features within 'AndroidCtrl' (e.g. wait durations, folder names, etc.).

> Will aim to have this as "up-to-date" as possible. However, see the actual python code for the actual names/functions/etc.

```mermaid
classDiagram
	class AndroidCtrl{
		+webdriver driver
		+webdriverwait phone_wait
		+AppiumService appium_service
		+bool internal_appium_service
		+int am_active
		+int background_view_active
	
		+quit()
		+back()
		+export_current_xml(parser, file)
		+android_background_app_view()
		+android_background_view_is_empty()
		+check_screen_is_homeview()
		+open_app_folder()
		+close_all_apps()
		+start_appium_service()
		+stop_appium_service()
	}
	class PhoneConfig {
		+dict capabilities
		+str appium_server_url
		+int phone_interaction_wait_time
    +str top_level_folder_name
	}
	AndroidCtrl *-- PhoneConfig
```
