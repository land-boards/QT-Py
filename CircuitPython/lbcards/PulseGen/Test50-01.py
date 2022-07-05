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

# Get three samples
# Make sure the three samples are within 10% of the average
# Return a value as a percent of the whole
def get_voltage(pin):
    got3GoodSamples = False
    while not got3GoodSamples:
        volts1 = pin.value
        volts2 = pin.value
        volts3 = pin.value
        avgVolts = (volts1 + volts2 + volts3) / 3
        if volts1 * 0.9 < avgVolts < volts1 * 1.1:
            if volts2 * 0.9 < avgVolts < volts2 * 1.1:
                if volts3 * 0.9 < avgVolts < volts3 * 1.1:
                    got3GoodSamples = True
    volts = (avgVolts * 3.3) / 65536
    percentVal = 100.0 * volts / 3.3
    return percentVal

print("Test Pulse Generator configured as 50 Ohm driver card")

outVal = False

while True:
    driveOut.value = outVal
    print(get_voltage(analog_in))
    time.sleep(1)
    outVal = not outVal
    