#!/usr/bin/env python

import brightness
import threading
import time

import pystray
from io import BytesIO
import cairosvg
from PIL import Image

#icon_path = "/usr/share/icons/breeze-dark/devices/22/video-display-brightness.svg"
#icon_path = "/usr/share/icons/breeze-dark/devices/32/video-display-brightness-symbolic.svg"
#icon_path = "/usr/share/icons/breeze-dark/status/32/input-keyboard-brightness.svg"
icon_path = "/usr/share/icons/breeze-dark/actions/24/brightness-high.svg"

prev_pause = None
prev_active = None
prev_last = None
prev_disp = None

def is_running_name():
    #print("check 1")
    return "Running" if (brightness.is_active and brightness.is_unpaused) else "Stopped"

def is_running_checked():
    #print("check 2")
    return True if (brightness.is_active and brightness.is_unpaused) else False

def get_value():
    #print("check 3")
    return f"Brightness: {brightness.last_brightness}"

def is_paused_checked():
    #print("check 4")
    return False if brightness.is_unpaused else True

def is_paused_name():
    #print("check 5")
    return "Unpaused" if brightness.is_unpaused else "Paused"

def toggle_pause():
    brightness.is_unpaused = False if brightness.is_unpaused else True

def quit(icon):
    print("stop brightness")
    brightness.running = False

    print("stop tray")
    icon.stop()

def poll(icon):
    global prev_pause, prev_active, prev_last, prev_disp

    while brightness.running:
        time.sleep(1.0)

        if (prev_pause == brightness.is_unpaused) and (prev_active == brightness.is_active) and (prev_last == brightness.last_brightness) and (prev_disp == brightness.disps):
            #print("skip")
            continue

        prev_pause = brightness.is_unpaused
        prev_active = brightness.is_active
        prev_last = brightness.last_brightness
        prev_disp = brightness.disps

        #print("update")
        icon.update_menu()

def display_menu():
    #print("menu")
    if (brightness.disps == None) or (len(brightness.disps) <= 0):
        return (pystray.MenuItem("No displays", None, enabled=False), )

    display_entries = []
    for d in brightness.disps:
        #s = "{} ({}) @ {}".format(d["name"], d["_id"], d["prev"])
        s = f"{d['prev']} @ {d['name']}"
        display_entries.append(pystray.MenuItem(s, None, enabled=False))

    return display_entries

def main():
    out = BytesIO()
    cairosvg.svg2png(url=icon_path, write_to=out)
    image = Image.open(out)

    print("start brightness")
    t_b = threading.Thread(target=brightness.main)
    t_b.start()

    print("prepare tray")
    icon = pystray.Icon("AutoBrightness", image, "AutoBrightness",
        menu=pystray.Menu(
            pystray.MenuItem(
                lambda icon=pystray.Icon: get_value(),
                None,
                enabled=False,
            ),
            pystray.MenuItem(
                "Displays",
                pystray.Menu(
                    lambda icon=pystray.Icon: display_menu(),
                )
            ),
            pystray.MenuItem(
                lambda icon=pystray.Icon: is_running_name(),
                None,
                enabled=False,
                checked=lambda icon=pystray.Icon: is_running_checked(),
            ),
            pystray.MenuItem(
                lambda icon=pystray.Icon: is_paused_name(),
                lambda icon=pystray.Icon: toggle_pause(),
                checked=lambda icon=pystray.Icon: is_paused_checked(),
            ),
            pystray.MenuItem(
                "Quit",
                lambda icon=pystray.Icon: quit(icon),
            ),
        )
    )

    print("start polling")
    t_p = threading.Thread(target=poll, args=(icon,))
    t_p.start()

    print("start tray")
    icon.run()

    print("join brightness")
    t_b.join()
    t_p.join()

    print("done")

if __name__ == "__main__":
    main()
