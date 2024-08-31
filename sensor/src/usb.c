/*
 * usb.c
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

#include <avr/wdt.h>

#include "usbdrv.h"
#include "osccal.c" // missing usbdrv include, so include here

#include "lux.h"
#include "main.h"

#define CUSTOM_RQ_ECHO 0 // send back wValue and wIndex, for testing comms reliability
#define CUSTOM_RQ_RESET 1 // reset to bootloader
#define CUSTOM_RQ_GET 2 // get ldr value, filtered

usbMsgLen_t usbFunctionSetup(uchar data[8]) {
    usbRequest_t *rq = (void *)data;
    static uchar dataBuffer[4]; // buffer must stay valid when usbFunctionSetup returns

    if (rq->bRequest == CUSTOM_RQ_ECHO) {
        // echo -- used for reliability tests
        dataBuffer[0] = rq->wValue.bytes[0];
        dataBuffer[1] = rq->wValue.bytes[1];
        dataBuffer[2] = rq->wIndex.bytes[0];
        dataBuffer[3] = rq->wIndex.bytes[1];

        usbMsgPtr = dataBuffer; // tell the driver which data to return
        return 4; // tell the driver to send 4 bytes
    } else if (rq->bRequest == CUSTOM_RQ_RESET) {
        // check for proper keys
        if ((rq->wValue.bytes[0] == 42) && (rq->wIndex.bytes[0] == 23)) {
            keep_feeding = false; // watchdog will trigger in one interval
            wdt_reset();

            dataBuffer[0] = 42; // send confirmation
        } else {
            dataBuffer[0] = 0; // error code
        }
        return 1;
    } else if (rq->bRequest == CUSTOM_RQ_GET) {
        uint16_t ldr_value = luxGet();
        dataBuffer[0] = (ldr_value & 0x00FF) >> 0;
        dataBuffer[1] = (ldr_value & 0xFF00) >> 8;

        usbMsgPtr = dataBuffer; // tell the driver which data to return
        return 2; // tell the driver to send 2 bytes
    }

    // default for not implemented requests: return no data back to host
    return 0;
}
