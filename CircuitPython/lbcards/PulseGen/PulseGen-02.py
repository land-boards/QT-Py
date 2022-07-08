# PulseGen-02.py
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
# Wiki page
#    http://land-boards.com/blwiki/index.php?title=MyMenu
#
# MyMenu MCP23008 GPIO Port Map
#     GP0 - LED D3
#     GP1 - LED D2
#     GP2 - LED D1
#     GP3 - Select button 0 = pressed
#     GP4 - Right button
#     GP5 - Down button
#     GP6 - Up button
#     GP7 - Left button
#
# Docs
# https://docs.circuitpython.org/projects/gps/en/latest/api.html#implementation-notes
# https://docs.circuitpython.org/projects/gps/en/latest/
# https://learn.adafruit.com/circuitpython-essentials/circuitpython-analog-in
#
# Wiring
# Signal   Color  From          To
#

import busio
import board
import time
from analogio import AnalogIn

import adafruit_ssd1306

analog_in = AnalogIn(board.A0)

MCP23008_IODIR = const(0x00)
MCP23008_IPOL = const(0x01)
MCP23008_GPINTEN = const(0x02)
MCP23008_DEFVAL = const(0x03)
MCP23008_INTCON = const(0x04)
MCP23008_IOCON = const(0x05)
MCP23008_GPPU = const(0x06)
MCP23008_INTF = const(0x07)
MCP23008_INTCAP = const(0x08)
MCP23008_GPIO = const(0x09)
MCP23008_OLAT = const(0x0A)

PB_NONE = const(0x00)
PB_SELECT=const(0x01)
PB_RIGHT=const(0x02)
PB_DOWN=const(0x04)
PB_UP=const(0x08)
PB_LEFT=const(0x10)

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

def writeMCP23xxxReg(reg, val):
    global i2cAddr_MCP23008
    passVal = bytearray([reg, val])
    while not i2c.try_lock():
        pass
    i2c.writeto(i2cAddr_MCP23008, passVal)
    i2c.unlock()

def readMCP23xxxReg(reg):
    global i2cAddr_MCP23008
    result = bytearray(1)
    while not i2c.try_lock():
        pass
    i2c.writeto_then_readfrom(i2cAddr_MCP23008, bytes([reg]), result)
    i2c.unlock()
    return result

def readPBs():
    rdVal = (int(readMCP23xxxReg(MCP23008_GPIO)[0]) >> 3) & 0x1F
    return rdVal

def writeLEDs(wrVal):
    writeMCP23xxxReg(MCP23008_OLAT, wrVal&0x07)

def initI2CIO8():
    writeMCP23xxxReg(MCP23008_IODIR, 0xF8)
    writeMCP23xxxReg(MCP23008_IPOL, 0xF8)
    writeMCP23xxxReg(MCP23008_GPINTEN, 0xF8)
    writeMCP23xxxReg(MCP23008_INTCON, 0x00)
    writeMCP23xxxReg(MCP23008_IOCON, 0x22)
    writeMCP23xxxReg(MCP23008_GPPU, 0x00)
    writeMCP23xxxReg(MCP23008_OLAT, 0x00)
    readMCP23xxxReg(MCP23008_GPIO)

def printToOLED(display,testStr):
    display.fill(0)
    try:
        display.text(testStr, 0, 0, 1)
        display.show()
    except FileNotFoundError:
        print(
            "To test the framebuf font setup, you'll need the font5x8.bin file from "
            + "https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/"
            + " in the same directory as this script"
        )

def scanI2C():
    # Auto-detect 
    while not i2c.try_lock():
        pass
    i2cAddrsFound = i2c.scan()
    i2c.unlock()
    return i2cAddrsFound

def findMCPI2CAddr(foundI2CDevices):
    for checkAddr in range(0x20,0x28):
        if checkAddr in foundI2CDevices:
            return(checkAddr)

i2c = busio.I2C(board.SCL, board.SDA)

display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

i2cAddrsFound = scanI2C()
# print("i2cAddrsFound =")
# for addr in i2cAddrsFound:
#     print(hex(addr),end=' ')
# print("")
i2cAddr_MCP23008 = findMCPI2CAddr(i2cAddrsFound)
# print("i2cAddr_MCP23008 =",hex(i2cAddr_MCP23008))
initI2CIO8()
writeLEDs(0)

printToOLED(display,"PulseGen Tester V1.0")
writeLEDs(1)
time.sleep(1)

stateGotLow = False
stateGotTerm = False
stateGotUnTerm = False
thresh = 25.0
term = 75.0

printToOLED(display,"Measure Freq")
time.sleep(1)
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
#print(freq,"Hz",end = '')
if 400 < freq < 700:
    printToOLED(display,"Freq in range")
else:
    printToOLED(display,"Freq out of range")
    assert False,"Out of freq range"
writeLEDs(2)
time.sleep(1)

printToOLED(display,"Looking for low")
time.sleep(1)
while not stateGotLow:
    readVal = get_voltage(analog_in)
    if readVal < thresh and not stateGotLow:
        printToOLED(display,"Got Low")
        stateGotLow = True
#         time.sleep(0.5)
writeLEDs(3)
time.sleep(1)

while (not stateGotTerm) or (not stateGotUnTerm):
    readVal = get_voltage(analog_in)
    if readVal > term and not stateGotUnTerm:
        printToOLED(display,"Got HIGH un-term")
        stateGotUnTerm = True
        time.sleep(0.5)
    elif (thresh < readVal < term) and not stateGotTerm:
        printToOLED(display,"Got HIGH term")
        stateGotTerm = True
        time.sleep(0.5)
    time.sleep(0.01) # Sleep for 1 mS
writeLEDs(4)
time.sleep(1)

printToOLED(display,"Detected all values")
writeLEDs(7)

while True:
    pass
