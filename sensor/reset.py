#!/usr/bin/env python

import usb.core
import usb.util

CUSTOM_RQ_ECHO = 0 # send back wValue and wIndex, for testing comms reliability
CUSTOM_RQ_RESET = 1 # reset to bootloader
CUSTOM_RQ_GET = 2 # get ldr value

def is_target_device(dev):
    if dev.manufacturer == "xythobuz.de" and dev.product == "AutoBrightness":
        return True
    return False

# find our device
dev = usb.core.find(idVendor=0x16c0, idProduct=0x05dc, custom_match=is_target_device)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# configure the device
dev.set_configuration()

# echo
r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, CUSTOM_RQ_ECHO, 42, 23, 4)
print("echo", r)

# reset
r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, CUSTOM_RQ_RESET, 0, 0, 1)
print("reset-err", r)

# value
r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, CUSTOM_RQ_GET, 0, 0, 2)
print("value", r)

# reset ok
r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, CUSTOM_RQ_RESET, 42, 23, 1)
print("reset-ok", r)
