#!/usr/bin/env python

import subprocess

def ddc_detect():
    r = subprocess.run(["ddcutil", "detect", "-t"], capture_output=True)
    if r.returncode != 0:
        raise ValueError("ddcutil returned {} \"{}\"".format(r.returncode))

    out = []

    displays = r.stdout.decode("utf-8").split("\n\n")
    for disp in displays:
        data = disp.split("\n")
        field = {}

        if len(data) < 4:
            continue

        # Display X
        num = data[0].split()
        if num[0] != "Display":
            #raise ValueError("unexpected identifier (\"{}\" != \"Display\")".format(num[0]))
            continue
        field["id"] = num[1]

        # Monitor: name ...
        name = data[3].split()
        if name[0] != "Monitor:":
            #raise ValueError("unexpected identifier (\"{}\" != \"Monitor:\")".format(name[0]))
            continue
        field["name"] = ' '.join(name[1:])

        out.append(field)

    return out

def ddc_get(dev):
    r = subprocess.run(["ddcutil", "-d", str(dev), "-t", "getvcp", "10"], capture_output=True)
    if r.returncode != 0:
        raise ValueError("ddcutil returned {} \"{}\"".format(r.returncode, r.stderr.decode("utf-8")))

    s = r.stdout.decode("utf-8").split()
    if (s[0] != "VCP") or (s[1] != "10") or (s[2] != "C") or (s[4] != "100"):
        raise ValueError("unexpected identifier \"{}\"".format(r.stdout.decode("utf-8")))

    return int(s[3])

def ddc_set(dev, val):
    val = int(val)
    if (val < 0) or (val > 100):
        raise ValueError("out of range")

    r = subprocess.run(["ddcutil", "-d", str(dev), "-t", "setvcp", "10", str(val)], capture_output=True)
    if r.returncode != 0:
        raise ValueError("ddcutil returned {} \"{}\"".format(r.returncode, r.stderr.decode("utf-8")))

if __name__ == "__main__":
    devs = ddc_detect()
    for dev in devs:
        print("Display:", dev["id"], dev["name"])

        b = ddc_get(dev["id"])
        print("Brightness:", b)

        new = 50
        if b == 50:
            new = 60
        print("Setting to {}...".format(new))
        ddc_set(dev["id"], new)

        b = ddc_get(dev["id"])
        print("Brightness:", b)

        print()
