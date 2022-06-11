"""Example for XIAO SAM and RP2040 boards. Blinks the built-in LED."""
import time
import board
import digitalio
 
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
 
while True:
    led.value = False   # low to turn on
    time.sleep(1.5)
    led.value = True    # high to turn off
    time.sleep(0.5)
