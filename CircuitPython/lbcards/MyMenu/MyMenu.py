# MyMenu_SWs.py
# Read 5 jumpers, write 3 LEDs
# Print to screen
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

import busio
import board
import time
#from digitalio import DigitalInOut
# Import the SSD1306 module.
import adafruit_ssd1306

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
i2cAddr_MCP23008 = findMCPI2CAddr(i2cAddrsFound)

def doLoop():
    initI2CIO8()
    
    # Bounce across the LEDs on the MyMenu card
    writeLEDs(1)
    time.sleep(0.25)
    writeLEDs(2)
    time.sleep(0.25)
    writeLEDs(4)
    time.sleep(0.25)
    writeLEDs(0)
    
    # Loop on read jumpers, write LEDs
    while True:
        rdVal = readPBs()
        if rdVal == 0X00:
            printToOLED(display,"No key pressed")
            writeLEDs(0)
        elif rdVal == 0X01:
            printToOLED(display,"Select pressed")
            writeLEDs(1)
            time.sleep(0.5)
            printToOLED(display,"Done!")
            writeLEDs(0)
            break
        elif rdVal == 0X02:
            printToOLED(display,"Right pressed")
            writeLEDs(2)
        elif rdVal == 0X04:
            printToOLED(display,"Down pressed")
            writeLEDs(3)
        elif rdVal == 0X08:
            printToOLED(display,"Up pressed")
            writeLEDs(4)
        elif rdVal == 0X10:
            printToOLED(display,"Left pressed")
            writeLEDs(5)
        else:
            printToOLED(display,"Multiple buttons pressed")
            writeLEDs(7)

doLoop()
