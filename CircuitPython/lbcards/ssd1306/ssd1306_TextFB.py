# ssd1306_TextFB.py
# SPDX-FileCopyrightText: Tony DiCola
# SPDX-License-Identifier: CC0-1.0

# Basic example of using framebuf capabilities on a SSD1306 OLED display.
# This example and library is meant to work with Adafruit CircuitPython API.

# Import all board pins.
import time
import board
import busio
from digitalio import DigitalInOut

# Import the SSD1306 module.
import adafruit_ssd1306

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
# The I2C address for these displays is 0x3d or 0x3c, change to match
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

print("Text test")
display.fill(0)
try:
    display.text("Line 1", 0, 0, 1)
    display.text("Line 2", 0, 1, 1)
    display.text("Line 3", 0, 2, 1)
    display.show()
    time.sleep(1)
    display.fill(0)
    char_width = 6
    char_height = 8
    chars_per_line = display.width // 6
    for i in range(255):
        x = char_width * (i % chars_per_line)
        y = char_height * (i // chars_per_line)
        display.text(chr(i), x, y, 1)
    display.show()
except FileNotFoundError:
    print(
        "To test the framebuf font setup, you'll need the font5x8.bin file from "
        + "https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/"
        + " in the same directory as this script"
    )
