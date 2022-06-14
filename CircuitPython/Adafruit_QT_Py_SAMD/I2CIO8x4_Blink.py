# I2CIO8x4_Blink.py
#
# Bounce a LED across multiple I2CIO-8 cards
# Uses (n) I2CIO-8 cards
# Auto-detects 1-8 cards
#  http://land-boards.com/blwiki/index.php?title=I2CIO-8
#
# https://docs.circuitpython.org/en/latest/shared-bindings/busio/index.html
# https://developer.sony.com/develop/spresense/docs/circuitpython_tutorials_en.html

import busio
import board
import time

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

def writeMCP23xxxReg(i2cAddr, reg, val):
    passVal = bytearray([reg, val])
    while not i2c.try_lock():
        pass
    i2c.writeto(i2cAddr, passVal)
    i2c.unlock()

def readMCP23xxxReg(i2cAddr, reg):
    result = bytearray(1)
    while not i2c.try_lock():
        pass
    i2c.writeto_then_readfrom(i2cAddr, bytes([reg]), result)
    return result
    i2c.unlock()

def readJumpers(i2cAddr):
    rdVal = int(readMCP23xxxReg(i2cAddr, MCP23008_GPIO)[0])
    rdVal = ((rdVal >> 4) & 0x0F)
    return rdVal

def writeLEDs(i2cAddr, wrVal):
    writeMCP23xxxReg(i2cAddr,MCP23008_OLAT, wrVal)

def initI2CIO8(i2cAddr):
    writeMCP23xxxReg(i2cAddr,MCP23008_IODIR, 0xF0)
    writeMCP23xxxReg(i2cAddr,MCP23008_IPOL, 0xF0)
    writeMCP23xxxReg(i2cAddr,MCP23008_GPINTEN, 0x0F)
    writeMCP23xxxReg(i2cAddr,MCP23008_INTCON, 0x00)
    writeMCP23xxxReg(i2cAddr,MCP23008_IOCON, 0x22)
    writeMCP23xxxReg(i2cAddr,MCP23008_GPPU, 0x00)

def i2cscan():
    i2cAddrList = []
    while not i2c.try_lock():
        pass
    try:
        i2cAddrList = i2c.scan()
    finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
        i2c.unlock()
    return i2cAddrList

i2c = busio.I2C(board.SCL, board.SDA)
i2cAddrList = i2cscan()
print("I2C addresses",i2cAddrList)

timeBetweenLEDs = 0.20

def doI2CIO8():
    for i2cAddr in i2cAddrList:
        initI2CIO8(i2cAddr)
    loopCount = 0
    while loopCount < 60:
        for i2cAddr in i2cAddrList:
            ledVal = 1
            while ledVal < 0x0F:
                writeLEDs(i2cAddr, ledVal)
                time.sleep( timeBetweenLEDs )
                ledVal <<= 1
            loopCount += 1
            writeLEDs(i2cAddr, 0)

doI2CIO8()
