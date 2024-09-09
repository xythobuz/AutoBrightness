#!/usr/bin/env python

import lux
import ddc
import time
import influx

filter_fact = 0.99

c_in = 0.6, -30.0, # in_a, in_b
calibration = {
    "HPN:HP 27xq:CNK1072BJY": [
        1.0, 10.0, # out_a, out_b
    ],

    "MSI:MSI G27CQ4:": [
        1.0, 0.0, # out_a, out_b
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
    last_brightness = brightness

    print()
    print("{}: Starting main loop".format(time.ctime()))
    print()

    time_brightness = time.time()
    time_displays = time.time()

    while True:
        # read brightness at approx. 1Hz with low-pass filtering
        time.sleep(1.0)
        brightness = filter_lux(brightness, lux.read_brightness(usb))

        # print brightness changes at most every 5s
        if (time.time() - time_brightness) > 5.0:
            time_brightness = time.time()

            if int(brightness) != last_brightness:
                last_brightness = int(brightness)
                print("{}: Brightness: {}".format(time.ctime(), last_brightness))

            try:
                influx.write("brightness,location=pc-back", "lux", brightness)

                for d in disps:
                    name = '_'.join(d["name"].split())
                    influx.write("brightness,location=" + name, "backlight", d["prev"])
            except:
                pass

        # set displays at most every 10s
        if (time.time() - time_displays) > 10.0:
            time_displays = time.time()

            for d in disps:
                val = lux_to_disp(d["name"], brightness)
                if val != d["prev"]:
                    try:
                        print("{}: Setting \"{}\" to {}".format(time.ctime(), d["name"], val))
                        ddc.ddc_set(d["_id"], val)
                        d["prev"] = val
                    except Exception as e:
                        print(e)
