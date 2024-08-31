/*
 * adc.c
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
#include <util/atomic.h>

#include "adc.h"

static uint32_t adc_value = 0;

void adcInit(void) {
    ADMUX = (1 << MUX0); // Vcc reference, ADC1 / PB2 in
    ADCSRA = (1 << ADEN) | (1 << ADIE) // adc and interrupt enabled
            | (1 << ADPS2) | (1 << ADPS1) // prescaler 64
            | (1 << ADSC); // start first conversion
}

static inline void adcFilter(uint16_t val) {
    adc_value = val; // TODO
}

ISR(ADC_vect) {
    // add this value to our filtered average
    adcFilter(ADC);

    // start next conversion
    ADCSRA |= (1 << ADSC);
}

uint32_t adcGet(void) {
    uint32_t val;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        val = adc_value;
    }
    return val;
}
