
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>
#include <util/delay.h>

#include "usbdrv.h"

usbMsgLen_t usbFunctionSetup(uchar data[8])
{
    return 0;   /* default for not implemented requests: return no data back to host */
}

int __attribute__((noreturn)) main(void) {
    wdt_enable(WDTO_1S);

    usbInit();

    usbDeviceDisconnect();  /* enforce re-enumeration, do this while interrupts are disabled! */
    wdt_reset();
    _delay_ms(255); /* fake USB disconnect for > 250 ms */
    usbDeviceConnect();

    sei();

    while (1) {
        wdt_reset();
        usbPoll();
    }
}
