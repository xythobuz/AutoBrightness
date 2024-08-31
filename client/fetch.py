#!/usr/bin/env python

import usb.core
import usb.util
import time

CUSTOM_RQ_ECHO = 0 # send back wValue and wIndex, for testing comms reliability
CUSTOM_RQ_RESET = 1 # reset to bootloader
CUSTOM_RQ_GET = 2 # get ldr value
CUSTOM_RQ_RAW = 3 # get ldr value

max_comm_retries = 5;

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

def read_val(req, w, a=0, b=0):
    for attempts in range(0, max_comm_retries):
        try:
            r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, req, a, b, w)
            return int.from_bytes(r, "little")
        except usb.core.USBError as e:
            if attempts >= (max_comm_retries - 1):
                raise e

# check for proper connectivity
if read_val(CUSTOM_RQ_ECHO, 4, 42, 23) != (42 | (23 << 16)):
    raise ValueError("invalid echo response")

# repeatedly print value
while True:
    v = read_val(CUSTOM_RQ_GET, 2)
    print(time.time(), ";", v, flush=True)

    #r = read_val(CUSTOM_RQ_RAW, 2)
    #print(time.time(), ";", r, flush=True)

    #print(time.time(), ";", v, ";", r, flush=True)

    time.sleep(0.25)
