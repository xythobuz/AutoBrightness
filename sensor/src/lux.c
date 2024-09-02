/*
 * lux.c
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

#include "twi.h"
#include "lux.h"

#define LUX_ADDR 0x23 //0x5C

#define OP_POWER_ON 0x01
#define OP_RESET 0x07

#define OP_CONT_1X 0x10
#define OP_CONT_0_5X 0x11
#define OP_CONT_4X 0x13

#define OP_ONCE_1X 0x20
#define OP_ONCE_0_5X 0x21
#define OP_ONCE_4X 0x23

void luxInit(void) {
    twiWrite(LUX_ADDR, OP_POWER_ON);
    twiWrite(LUX_ADDR, OP_CONT_0_5X);
}

uint16_t luxGet(void) {
    uint16_t val = twiRead(LUX_ADDR);
    return val;
}
