# PulseGen-01.py
# Test PulseGen card
# http://land-boards.com/blwiki/index.php?title=PulseGen
# 
# Reads PulseGen output as analog value
# Test with/without 50 ohm terminator
# Should be ~1/2 of 3.3V when terminator is installed
#
# On QTPy49 breakout card
# http://land-boards.com/blwiki/index.php?title=QTPy49
# Runs on XIAO RP2040 board
# http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)
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
# import digitalio

analog_in = AnalogIn(board.A0)

# driveOut = digitalio.DigitalInOut(board.D1)
# driveOut.direction = digitalio.Direction.OUTPUT
# outVal = False

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

print("PulseGen Card Tester V1.0")

stateGotLow = False
stateGotTerm = False
stateGotUnTerm = False
thresh = 25.0
term = 75.0

print("Measuring Frequency, ",end='')
while get_voltage(analog_in) > thresh:
    pass
while get_voltage(analog_in) < thresh:
    pass
startTime = time.monotonic_ns()
while get_voltage(analog_in) > thresh:
    pass
endTime = time.monotonic_ns()
deltaTime = endTime - startTime
# print(deltaTime,"nS")
period = 2 * deltaTime
freq = 1000000000 / period
print(freq,"Hz",end = '')
if 400 < freq < 700:
    print(" is in expected range")
else:
    print(" is out of expected range")
    assert False,"Out of freq range"

print("Looking for low...",end='')
while not stateGotLow:
    readVal = get_voltage(analog_in)
    if readVal < thresh and not stateGotLow:
        print("Got Low val",readVal,end='')
        print("%")
        stateGotLow = True
        time.sleep(0.5)

while (not stateGotTerm) or (not stateGotUnTerm):
    readVal = get_voltage(analog_in)
    if readVal > term and not stateGotUnTerm:
        print("Got HIGH un-terminated val",readVal,end='')
        print("%")
        stateGotUnTerm = True
        time.sleep(0.5)
    elif (thresh < readVal < term) and not stateGotTerm:
        print("Got HIGH terminated val",readVal,end='')
        print("%")
        stateGotTerm = True
        time.sleep(0.5)
    time.sleep(0.01) # Sleep for 1 mS

print("Detected all values")
