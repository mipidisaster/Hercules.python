#!/usr/bin/env python
# Configuration file for the "AndroidCtrl" class within this package.
#

# Notes to help determine 'x'/'y' orientation
# Top left - x=0, y=0
# Top right - x=full, y=0
# Bottom left - x=0, y=full
# Bottom right - x=full, y=full



class PhoneConfig:
    capabilities = dict(
        platformName='Android',
        deviceName='Android Emulator',
        automationName='uiautomator2',
        newCommandTimeout=6000,             # Increase the timeout period, to allow for slow debugging
    )

    appium_server_url = 'http://localhost:4723'

    phone_interaction_wait_time = 15        # seconds