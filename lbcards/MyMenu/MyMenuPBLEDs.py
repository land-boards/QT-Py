# MyMenuPBLEDs - Test MyMenu cards switches and LEDs
#
# Read switches, Light LEDs in pattern that shows which was pressed
#
# https://docs.circuitpython.org/en/latest/shared-bindings/busio/index.html
# https://developer.sony.com/develop/spresense/docs/circuitpython_tutorials_en.html
#
# import MyMenuPBLEDs
# MyMenuPBLEDs.doI2CIO8()
# http://land-boards.com/blwiki/index.php?title=MyMenu
# GPIO Port Map
# GP0 - LED D3
# GP1 - LED D2
# GP2 - LED D1
# GP3 - Select button 0 = pressed
# GP4 - Right button
# GP5 - Down button
# GP6 - Up button
# GP7 - Left button
#

import busio
import board
# import time

MCP23008_BASEADDR = 0x20
MCP23008_IODIR = 0x00
MCP23008_IPOL = 0x01
MCP23008_GPINTEN = 0x02
MCP23008_DEFVAL = 0x03
MCP23008_INTCON = 0x04
MCP23008_IOCON = 0x05
MCP23008_GPPU = 0x06
MCP23008_INTF = 0x07
MCP23008_INTCAP = 0x08
MCP23008_GPIO = 0x09
MCP23008_OLAT = 0x0A

def writeMCP23xxxReg(reg, val):
    passVal = bytearray([reg, val])
    i2c.writeto(MCP23008_BASEADDR, passVal)

def readMCP23xxxReg(reg):
    result = bytearray(1)
    i2c.writeto_then_readfrom(MCP23008_BASEADDR, bytes([reg]), result)
    return result

def readSwitches():
    rdVal = int(readMCP23xxxReg(MCP23008_GPIO)[0])
    rdVal = ((rdVal >> 3) & 0x1F)
    return rdVal

def writeLEDs(wrVal):
    writeMCP23xxxReg(MCP23008_OLAT, wrVal & 0x7)

def initI2CIO8():
    # Bits 0-3 are outputs, Bits 3-7 are inputs
    writeMCP23xxxReg(MCP23008_IODIR, 0xf8)
    writeMCP23xxxReg(MCP23008_IPOL, 0xF8)
    writeMCP23xxxReg(MCP23008_GPINTEN, 0xF8)
    writeMCP23xxxReg(MCP23008_INTCON, 0x00)
    # No SEQOP - Sequential ops not
    # DISSLW - No slew rate cpmtrol
    # ODR - active drive INT
    # INTPOL - Avtive high interrupts
    writeMCP23xxxReg(MCP23008_IOCON, 0x32)
    writeMCP23xxxReg(MCP23008_GPPU, 0x00)

i2c = busio.I2C(board.SCL, board.SDA)

def doI2CIO8():
    # Lock the I2C device before accessing I2C
    # print("Running")
    while not i2c.try_lock():
        pass

    # print("Init")
    initI2CIO8()

    # print("Loop")
    while True:
        swVals = readSwitches()
        if swVals == 0x00:
            writeLEDs(0)
        elif swVals == 0x01:
            writeLEDs(1)
        elif swVals == 0x02:
            writeLEDs(2)
        elif swVals == 0x04:
            writeLEDs(3)
        elif swVals == 0x08:
            writeLEDs(4)
        elif swVals == 0x10:
            writeLEDs(5)
        else:
            writeLEDs(7)
        # print(swVals)

    i2c.unlock()
