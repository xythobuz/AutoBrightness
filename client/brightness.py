#!/usr/bin/env python

import lux
import ddc
import influx
import window

import time
import sys
import select

import paho.mqtt.publish as publish

MQTT_HOST = "MQTT_HOST_HERE"
MQTT_USER = "MQTT_USERNAME_HERE"
MQTT_PASS = "MQTT_PASSWORD_HERE"

filter_fact = 0.90

c_in = [ 0.6, -30.0 ] # in_a, in_b
calibration = {
    "HPN:HP 27xq:CNK1072BJY": [
        1.0, 10.0, # out_a, out_b
    ],

    "MSI:MSI G27CQ4:": [
        1.0, 0.0, # out_a, out_b
    ],
}

running = True
is_active = True
is_unpaused = True
last_brightness = 0
disps = None
want_reset = False

def cal(v, c):
    # out = out_b + out_a * in_a * max(0, in_b + in)
    return c[1] + c[0] * c_in[0] * max(0, c_in[1] + v)

def filter_lux(old, new):
    return max(0.1, (old * filter_fact) + (new * (1.0 - filter_fact)))

def lux_to_disp(name, val):
    if name in calibration:
        val = cal(int(val), calibration[name])
    else:
        #raise ValueError("no calibration for \"{}\"".format(name))
        val = cal(int(val), [1.0, 0.0]) # default when no calibration
    val = int(val)
    return min(max(val, 0), 100)

def main():
    global running, is_active, is_unpaused, last_brightness, disps, want_reset

    print("usb init")
    usb = lux.usb_init()
    print("check usb connection")
    lux.check_connection(usb)

    print("detect displays")
    disps = ddc.ddc_detect()
    if len(disps) <= 0:
        raise ValueError("no displays found")

    print("query displays")
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
    time_displays = time.time() - 8.0
    time_window = time.time()

    is_active = True
    is_unpaused = True
    want_reset = False

    while running:
        # read brightness at approx. 1Hz with low-pass filtering
        time.sleep(1.0)
        brightness = filter_lux(brightness, lux.read_brightness(usb))

        if (select.select([sys.stdin, ], [], [], 0.0)[0]) or want_reset:
            if want_reset:
                want_reset = False
            else:
                line = sys.stdin.readline()
            print("Resetting displays")
            for d in disps:
                try:
                    ddc.ddc_set(d["_id"], d["prev"])
                except Exception as e:
                    print(e)

        # print/store/transmit brightness changes at most every 30s
        if (time.time() - time_brightness) > 30.0:
            time_brightness = time.time()

            if int(brightness) != last_brightness:
                last_brightness = int(brightness)
                print("{}: Brightness: {}".format(time.ctime(), last_brightness))

            msgs = [{
                'topic': "livingroom/brightness/lux",
                'payload': str(brightness),
                'qos': 0,
                'retain': True,
            }]
            for d in disps:
                name = '_'.join(d["name"].split())
                msgs.append({
                    'topic': f"livingroom/brightness/{name}",
                    'payload': str(d["prev"]),
                    'qos': 0,
                    'retain': True,
                })
            try:
                publish.multiple(msgs, hostname=MQTT_HOST, client_id="AutoBrightness", auth={
                    'username': MQTT_USER,
                    'password': MQTT_PASS,
                })
            except:
                pass

            try:
                influx.write("brightness,location=pc-back", "lux", brightness)

                for d in disps:
                    name = '_'.join(d["name"].split())
                    influx.write("brightness,location=" + name, "backlight", d["prev"])
            except:
                pass

        # check for fullscreen windows every 20s
        if (time.time() - time_window) > 20.0:
            time_window = time.time()
            info = window.query()

            if info["fullscreen"] and is_active:
                print("{}: App \"{}\" is now fullscreen! Pausing.".format(time.ctime(), info["name"]))

            if (not info["fullscreen"]) and (not is_active):
                print("{}: No longer fullscreen. Continuing.".format(time.ctime()))

                # re-apply previous brightness values soon
                for d in disps:
                    d["prev"] = -1

            is_active = not info["fullscreen"]

        # set displays at most every 10s
        if is_active and is_unpaused and ((time.time() - time_displays) > 10.0):
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

                        # set to zero to show display is disconnected
                        d["prev"] = -1

if __name__ == "__main__":
    main()
