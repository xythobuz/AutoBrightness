#!/usr/bin/env python

import lux
import ddc
import time

filter_fact = 0.9

# out = out_b + out_a * in_a * (in_b + in)
c_in = 1.0, -40.0, # in_a, in_b
calibration = {
    "HPN:HP 27xq:CNK1072BJY": [
        1.0, 30.0, # out_a, out_b
    ],

    "MSI:MSI G27CQ4:": [
        1.0, 20.0, # out_a, out_b
    ],
}

def cal(v, c):
    return c[1] + c[0] * c_in[0] * (c_in[1] + v)

def filter_lux(old, new):
    return (old * filter_fact) + (new * (1.0 - filter_fact))

def lux_to_disp(name, val):
    if name in calibration:
        val = cal(int(val), calibration[name])
    else:
        raise ValueError("no calibration for \"{}\"".format(name))
    val = int(val)
    return min(max(val, 0), 100)

if __name__ == "__main__":
    usb = lux.usb_init()
    lux.check_connection(usb)

    disps = ddc.ddc_detect()
    brightness = lux.read_brightness(usb)
    print("Brightness:", brightness)

    for d in disps:
        d["prev"] = ddc.ddc_get(d["id"])
        print("Display \"{}\" at {}".format(d["name"], d["prev"]))

    print()
    print("Starting main loop")
    print()

    while True:
        brightness = filter_lux(brightness, lux.read_brightness(usb))

        for d in disps:
            val = lux_to_disp(d["name"], brightness)
            if val != d["prev"]:
                d["prev"] = val
                print("Setting \"{}\" to {}".format(d["name"], val))
                ddc.ddc_set(d["id"], val)

        time.sleep(1.0)
