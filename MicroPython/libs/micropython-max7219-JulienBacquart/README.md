
Micropython library for a 8 digits 7-segment display based on the MAX7219.

Thanks to https://github.com/adafruit/micropython-adafruit-max7219 for getting me started.

# Wiring:

| ESP8266        | MAX7219 |
| ---------      | ------- |
| HMOSI (GPIO13) | DIN     |
| HSCLK (GPIO14) | CLK     |
| I/O (GPIO15)   | CS      |

The I/0 pin can be moved to any other pin.

I'm using the hardware SPI, but it can be moved to any other pin using the software SPI.

# Example of use:

    from machine import Pin, SPI
    import max7219

    hspi = SPI(1, baudrate=10000000, polarity=0, phase=0)
    display = max7219.Max7219(hspi, Pin(15))
    display.clear()
    display.write_hex(0xAB9F)