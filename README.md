# AutoBrightness

Simple solution to measure ambient room lighting conditions with an AtTiny85 based USB lux sensor and set external display backlight intensity accordingly via DDC/CI.

See [this blog post for details](https://www.xythobuz.de/auto_brightness.html).

## Sensor

Uses a [Digispark Rev. 3 clone](https://www.az-delivery.de/en/products/digispark-board) with a [GY-302 BH1750 breakout board](https://www.az-delivery.de/en/products/gy-302-bh1750-lichtsensor-lichtstaerke-modul-fuer-arduino-und-raspberry-pi) connected to the I2C bus.

[![Front of PCB](https://www.xythobuz.de/img/autobrightness_pcb_1_small.jpg)](https://www.xythobuz.de/img/autobrightness_pcb_1.jpg)
[![Back of PCB](https://www.xythobuz.de/img/autobrightness_pcb_2_small.jpg)](https://www.xythobuz.de/img/autobrightness_pcb_2.jpg)

### Quick Start

Check out the repo and required submodules.

    git clone https://git.xythobuz.de/thomas/AutoBrightness.git
    cd AutoBrightness
    git submodule update --init

Build the firmware and upload it.

    make -C sensor upload

Prepare udev rules for our new device.

    sudo cp sensor/49-autobrightness.rules /etc/udev/rules.d/49-autobrightness.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger

## Client

### Quick Start

Install dependency and run the client.

    yay -S python-pyusb
    ./client/brightness.py

## License

The firmware of this project is licensed as GPLv3.
A copy of the license can be found in `COPYING`.

It uses [V-USB](https://github.com/obdev/v-usb) and is based on their example code.

Also includes the I2C Master implementation from the Atmel AVR310 AppNote.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    See <http://www.gnu.org/licenses/>.
