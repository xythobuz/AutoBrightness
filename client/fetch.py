#!/usr/bin/env python

import usb.core
import usb.util
import time

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

def read_u32(req, a=0, b=0):
    r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, req, a, b, 4)
    return int.from_bytes(r, "little")

# check for proper connectivity
if read_u32(CUSTOM_RQ_ECHO, 42, 23) != (42 | (23 << 16)):
    raise ValueError("invalid echo response")

# repeatedly print value
while True:
    r = read_u32(CUSTOM_RQ_GET)
    print(time.time(), ";", r, flush=True)
    time.sleep(0.25)
