#!/usr/bin/env python

import usb.core
import usb.util
import time

CUSTOM_RQ_ECHO = 0 # send back wValue and wIndex, for testing comms reliability
CUSTOM_RQ_RESET = 1 # reset to bootloader
CUSTOM_RQ_GET = 2 # get ldr value

max_comm_retries = 5;

def is_target_device(dev):
    if dev.manufacturer == "xythobuz.de" and dev.product == "AutoBrightness":
        return True
    return False

def usb_init():
    # find our device
    dev = usb.core.find(idVendor=0x16c0, idProduct=0x05dc, custom_match=is_target_device)

    # was it found?
    if dev is None:
        raise ValueError('Device not found')

    # configure the device
    dev.set_configuration()

    return dev

def read_val(dev, req, w, a=0, b=0):
    for attempts in range(0, max_comm_retries):
        try:
            r = dev.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_IN, req, a, b, w)
            return int.from_bytes(r, "little")
        except usb.core.USBError as e:
            if attempts >= (max_comm_retries - 1):
                raise e

def check_connection(dev):
    # check for proper connectivity
    if read_val(dev, CUSTOM_RQ_ECHO, 4, 42, 23) != (42 | (23 << 16)):
        raise ValueError("invalid echo response")

def read_brightness(dev):
    return read_val(dev, CUSTOM_RQ_GET, 2)

if __name__ == "__main__":
    dev = usb_init()
    check_connection(dev)

    # repeatedly print value
    while True:
        v = read_brightness(dev)
        print(time.time(), ";", v, flush=True)
        time.sleep(0.25)
