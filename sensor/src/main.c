/*
 * main.c
 *
 * Copyright (c) 2024 Thomas Buck (thomas@xythobuz.de)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * See <http://www.gnu.org/licenses/>.
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>
#include <util/delay.h>

#include "adc.h"
#include "usbdrv.h"

int __attribute__((noreturn)) main(void) {
    wdt_enable(WDTO_1S);
    wdt_reset();

    // status LED
    DDRB |= (1 << DDB1); // output
    PORTB |= (1 << PB1); // turn on

    adcInit();
    usbInit();

    usbDeviceDisconnect(); // enforce re-enumeration, do this while interrupts are disabled!
    wdt_reset();
    _delay_ms(255); // fake USB disconnect for > 250 ms
    usbDeviceConnect();

    PORTB &= ~(1 << PB1); // turn status LED off

    // enable interrupts and enter main loop for USB polling
    sei();
    while (1) {
        wdt_reset();
        usbPoll();
    }
}
