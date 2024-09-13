#!/usr/bin/env python

import os
import subprocess
from datetime import datetime
import json
import time

max_comm_retries = 5

# https://unix.stackexchange.com/a/776620
def query_internal(verbose=False):
    dir_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(dir_path, "kwin_check.js")
    datetime_now = datetime.now()

    result = subprocess.run("dbus-send --print-reply --dest=org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript string:" + file_path, capture_output=True, shell=True)
    if verbose and result.stdout:
        print("Output 1", result.stdout.decode("utf-8"))
    if verbose and result.stderr:
        print("Errs 1", result.stderr.decode("utf-8"))

    n = result.stdout.decode("utf-8").split("\n")[1].split()[1]
    if verbose:
        print("Script ID", n)

    result = subprocess.run("dbus-send --print-reply --dest=org.kde.KWin /Scripting/Script" + n + " org.kde.kwin.Script.run", capture_output=True, shell=True)
    if verbose and result.stdout:
        print("Output 2", result.stdout.decode("utf-8"))
    if verbose and result.stderr:
        print("Errs 2", result.stderr.decode("utf-8"))

    result = subprocess.run("dbus-send --print-reply --dest=org.kde.KWin /Scripting/Script" + n + " org.kde.kwin.Script.stop", capture_output=True, shell=True)
    if verbose and result.stdout:
        print("Output 3", result.stdout.decode("utf-8"))
    if verbose and result.stderr:
        print("Errs 3", result.stderr.decode("utf-8"))

    since = str(datetime_now)

    result = subprocess.run("journalctl _COMM=kwin_wayland -o cat --since \"" + since + "\"", capture_output=True, shell=True)
    if verbose and result.stdout:
        print("Output 4", result.stdout.decode("utf-8"))
    if verbose and result.stderr:
        print("Errs 4", result.stderr.decode("utf-8"))

    msg = result.stdout.decode().rstrip().split("\n")[0][4:]
    try:
        return json.loads(msg)
    except Exception as e:
        print("Failed msg: \"{}\"".format(msg))
        raise e

def query(verbose=False):
    for attempts in range(0, max_comm_retries):
        try:
            return query_internal(verbose)
        except Exception as e:
            if attempts >= (max_comm_retries - 1):
                raise e
            else:
                time.sleep(0.5)

if __name__ == "__main__":
    info = query()
    print("Name: \"{}\"".format(info["name"]))
    print("PID: {}".format(info["pid"]))
    print("Fullscreen: {}".format(info["fullscreen"]))
