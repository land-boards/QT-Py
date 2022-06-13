# MyMenu_SWs.py
# http://land-boards.com/blwiki/index.php?title=MyMenu
#
# GPIO Port Map
#     GP0 - LED D3
#     GP1 - LED D2
#     GP2 - LED D1
#     GP3 - Select button 0 = pressed
#     GP4 - Right button
#     GP5 - Down button
#     GP6 - Up button
#     GP7 - Left button

# I2CIO8_RW.py
# Read 4 jumpers, write 4 LEDs
#
# https://docs.circuitpython.org/en/latest/shared-bindings/busio/index.html
# https://developer.sony.com/develop/spresense/docs/circuitpython_tutorials_en.html

import busio
import board
import time

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
    global i2cAddr_MCP23008
    passVal = bytearray([reg, val])
    i2c.writeto(i2cAddr_MCP23008, passVal)

def readMCP23xxxReg(reg):
    global i2cAddr_MCP23008
    result = bytearray(1)
    i2c.writeto_then_readfrom(i2cAddr_MCP23008, bytes([reg]), result)
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

i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass

# Auto-detect 
i2cAddrsFound = i2c.scan()
for checkAddr in range(0x20,0x28):
    if checkAddr in i2cAddrsFound:
        i2cAddr_MCP23008 = checkAddr
        print("Card found at i2c address",i2cAddr_MCP23008)

def doLoop():
    print("Card is at i2c address",i2cAddr_MCP23008)
    # Lock the I2C device before accessing I2C
#     while not i2c.try_lock():
#         pass

    print("unlocked")
    # Initialize the I2CIO-8 card
    print("call initI2CIO8()")
    initI2CIO8()
    print("done with initI2CIO8()")
    
    for countVal in range(1,0x08):
        writeLEDs(countVal)
        time.sleep(0.25)
    writeLEDs(0)

    # Loop on read jumpers, write LEDs
    while True:
        rdVal = readPBs()
#        print("rdVal",rdVal)
#        time.sleep(0.25)
        if rdVal == 0X00:
#             print("Select")
            writeLEDs(0)
        elif rdVal == 0X01:
#             print("Select")
            writeLEDs(1)
        elif rdVal == 0X02:
#             print("Right")
            writeLEDs(2)
        elif rdVal == 0X04:
#             print("Down")
            writeLEDs(3)
        elif rdVal == 0X08:
#             print("Up")
            writeLEDs(4)
        elif rdVal == 0X10:
#             print("Left")
            writeLEDs(5)
        else:
            writeLEDs(7)

    i2c.unlock()

doLoop()
