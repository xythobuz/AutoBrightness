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

        for d in data:
            v = d.split()
            if v[0] == "Display":
                field["id"] = v[1]
            elif (v[0] == "I2C") and (v[1] == "bus:"):
                field["bus"] = v[2]
            elif v[0] == "Monitor:":
                field["name"] = ' '.join(v[1:])

        # if id is not there it's an "Ivalid display"
        if "id" in field:
            out.append(field)

    return out

def ddc_get(dev):
    if dev.startswith("/dev/i2c-"):
        cmd = ["ddcutil", "--skip-ddc-checks", "--bus", dev.replace("/dev/i2c-", ""), "-t", "getvcp", "10"]
    else:
        cmd = ["ddcutil", "-d", str(dev), "-t", "getvcp", "10"]

    r = subprocess.run(cmd, capture_output=True)
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

    if dev.startswith("/dev/i2c-"):
        cmd = ["ddcutil", "--noverify", "--bus", dev.replace("/dev/i2c-", ""), "-t", "setvcp", "10", str(val)]
    else:
        cmd = ["ddcutil", "--noverify", "-d", str(dev), "-t", "setvcp", "10", str(val)]

    r = subprocess.run(cmd, capture_output=True)
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
