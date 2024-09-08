#!/usr/bin/env python

import lux
import ddc
import time

filter_fact = 0.9

c_in = 0.6, -60.0, # in_a, in_b
calibration = {
    "HPN:HP 27xq:CNK1072BJY": [
        1.0, 30.0, # out_a, out_b
    ],

    "MSI:MSI G27CQ4:": [
        1.0, 20.0, # out_a, out_b
    ],
}

def cal(v, c):
    # out = out_b + out_a * in_a * max(0, in_b + in)
    return c[1] + c[0] * c_in[0] * max(0, c_in[1] + v)

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
    if len(disps) <= 0:
        raise ValueError("no displays found")

    for d in disps:
        # select i2c bus if available, id otherwise
        if "bus" in d:
            d["_id"] = d["bus"]
        else:
            d["_id"] = d["id"]

        # get initial value
        d["prev"] = ddc.ddc_get(d["_id"])
        print("Display \"{}\" ({}) at {}".format(d["name"], d["_id"], d["prev"]))

    brightness = lux.read_brightness(usb)
    print("Brightness:", brightness)

    print()
    print("{}: Starting main loop".format(time.ctime()))
    print()

    while True:
        brightness = filter_lux(brightness, lux.read_brightness(usb))

        for d in disps:
            val = lux_to_disp(d["name"], brightness)
            if val != d["prev"]:
                d["prev"] = val
                print("{}: Setting \"{}\" to {}".format(time.ctime(), d["name"], val))
                ddc.ddc_set(d["_id"], val)

        time.sleep(1.0)
