# RGBLED.py - Blinks the built-in LED
# Example for XIAO SAM and RP2040 boards

import time
import board
import digitalio

ledRed = digitalio.DigitalInOut(board.LED_RED)
ledRed.direction = digitalio.Direction.OUTPUT
ledGreen = digitalio.DigitalInOut(board.LED_GREEN)
ledGreen.direction = digitalio.Direction.OUTPUT
ledBlue = digitalio.DigitalInOut(board.LED_BLUE)
ledBlue.direction = digitalio.Direction.OUTPUT

while True:
    ledBlue.value = True    # high to turn off
    ledRed.value = False   # low to turn on
    time.sleep(1.0)
    ledRed.value = True    # high to turn off
    ledGreen.value = False   # low to turn on
    time.sleep(1.0)
    ledGreen.value = True    # high to turn off
    ledBlue.value = False   # low to turn on
    time.sleep(1.0)
