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

def is_running():
    #print("check1")
    return "Active" if brightness.is_active else "Inactive"

def get_value():
    #print("check2")
    return f"Brightness: {brightness.last_brightness}"

def quit(icon):
    print("stop brightness")
    brightness.running = False

    print("stop tray")
    icon.stop()

def poll(icon):
    while brightness.running:
        #print("update")
        icon.update_menu()
        time.sleep(5.0)

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
                'Activated',
                None,
                enabled=False,
                checked=lambda icon=pystray.Icon: is_running(),
            ),

            pystray.MenuItem(
                lambda icon=pystray.Icon: get_value(),
                None,
                enabled=False,
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
