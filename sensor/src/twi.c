/*
 * twi.c
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

#include "USI_TWI_Master.h"
#include "twi.h"

void twiInit(void) {
    USI_TWI_Master_Initialise();
}

void twiWrite(uint8_t addr, uint8_t op) {
    uint8_t msg[] = {
        addr << TWI_ADR_BITS,
        op
    };

    USI_TWI_Start_Transceiver_With_Data(msg, sizeof(msg));
}

uint16_t twiRead(uint8_t addr) {
    uint8_t msg[] = {
        (addr << TWI_ADR_BITS) | (1 << TWI_READ_BIT),
        0, 0 // space for received data
    };

    do {
        USI_TWI_Start_Transceiver_With_Data(msg, sizeof(msg));
    } while (USI_TWI_Get_State_Info() == USI_TWI_NO_ACK_ON_ADDRESS);

    return (msg[1] << 8) | msg[2];
}
