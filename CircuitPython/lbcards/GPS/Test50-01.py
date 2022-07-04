# Test50-01.py
# PulseGen configured as 50 Ohm Driver
# http://land-boards.com/blwiki/index.php?title=PulseGen
# 
# Sends pulse to Input of PulseGen 
# Reads PulseGen output as analog value
# Test with/without 50 ohm terminator
# Should be ~1/2 of 3.3V when terminator is installed
#
# Runs on XIAO RP2040 board
# http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)
# On QTPy49 card
# http://land-boards.com/blwiki/index.php?title=QTPy49
# 
# Based on
#
# Docs
# https://docs.circuitpython.org/projects/gps/en/latest/api.html#implementation-notes
# https://docs.circuitpython.org/projects/gps/en/latest/
# https://learn.adafruit.com/circuitpython-essentials/circuitpython-analog-in
# 
# Wiring
# Signal   Color  From          To

import time
import board
from analogio import AnalogIn
import digitalio

analog_in = AnalogIn(board.A0)

driveOut = digitalio.DigitalInOut(board.D1)
driveOut.direction = digitalio.Direction.OUTPUT

def get_voltage(pin):
    volts = (pin.value * 3.3) / 65536
    percentVal = 100.0 * volts / 3.3
    return percentVal

print("Test Pulse Generator configured as 50 Ohm driver card")

outVal = False

while True:
    driveOut.value = outVal
    print(get_voltage(analog_in))
    time.sleep(1)
    outVal = not outVal
    