# SDLoader_V2.py
# SD card with MyMenu card
# Runs under CircuitPython 7.x
#
# https://learn.adafruit.com/micropython-hardware-ssd1306-oled-display/circuitpython
#

import board
import busio
import sdcardio
import storage
import os
import adafruit_ssd1306
import time

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

MyMenu_SELECT_BIT = const(0x01)
MyMenu_RIGHT_BIT = const(0x02)
MyMenu_DOWN_BIT = const(0x04)
MyMenu_UP_BIT = const(0x08)
MyMenu_LEFT_BIT = const(0x10)

MyMenu_NONE = const(0x00)
MyMenu_SELECT = const(0x01)
MyMenu_RIGHT = const(0x02)
MyMenu_DOWN = const(0x03)
MyMenu_UP = const(0x04)
MyMenu_LEFT = const(0x05)

# MyMenu code follows

def waitPB():
    PBs = MyMenu_NONE
    while PBs == MyMenu_NONE:
        PBs = pollPBVals()
        time.sleep(0.01)
#     print("waitPB(): PBs",PBs)
    while pollPBVals() != MyMenu_NONE:
        pass
#     assert False,"waitPB(): stop"
    return PBs

def pollPBVals():
    kbVal = readPBs()
#     if kbVal != 0:
#         print("pollPBVals(): kbVals",kbVal)
    if kbVal == 0:
        return MyMenu_NONE
    elif kbVal == MyMenu_SELECT_BIT:
        return MyMenu_SELECT
    elif kbVal == MyMenu_RIGHT_BIT:
        return MyMenu_RIGHT
    elif kbVal == MyMenu_DOWN_BIT:
        return MyMenu_DOWN
    elif kbVal == MyMenu_UP_BIT:
        return MyMenu_UP
    elif (kbVal and MyMenu_LEFT_BIT) == MyMenu_LEFT_BIT:
        return MyMenu_LEFT
    return MyMenu_NONE

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

def clearDisplay(display):
    display.fill(0)

def printToOLED(display,xCell,yCell,testStr):
    try:
        display.text(testStr, xCell*5, yCell<<3, 1)
    except FileNotFoundError:
        print(
            "To test the framebuf font setup, you'll need the font5x8.bin file from "
            + "https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/"
            + " in the same directory as this script"
        )

def displayOLED():
    try:
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

# SD card code

def writeFile():
    with open("/sd/test.txt", "w") as f:
        f.write("Hello world!\r\n")

def readPrintFileLine():
    with open("/sd/test.txt", "r") as f:
        print("Read line from file:")
        print(f.readline(), end='')

def readPrintFileLines():
    with open("/sd/test.txt", "r") as f:
        print("Printing lines in file:")
        line = f.readline()
        for line in f:
            print(line, end='')

def getListOfFolders(path):
    global listOfFolders
    tabs = 0
    if path not in listOfFolders:
        if path != '/sd/System Volume Information':
            listOfFolders.append(path + '/')
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        isdir = stats[0] & 0x4000
        if isdir:
            getListOfFolders(path + "/" + file)

def print_directory(path, tabs=0):
    global dirFileNames
    global listOfFolders
    if path not in listOfFolders:
        listOfFolders.append(path)
    for file in os.listdir(path):
        dirFileNames.append((path,file))
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

#         prettyprintname = ""
#         for _ in range(tabs):
#             prettyprintname += "   "
#         prettyprintname += file
#         if isdir:
#             prettyprintname += "/"
        #print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)

# selectFolder() - Select the folder and return the path
def selectFolder():
    global listOfFolders
    foldersCount = len(listOfFolders)
    print("Folders count", foldersCount)
    print("Folders")
    print(listOfFolders)
    screenCount = int((foldersCount+5)/6)
    print("screenCount",screenCount)
    for screenNum in range(0,screenCount):
        activeLine = 1
        selectNext = False
        while not selectNext:
            clearDisplay(display)
            printToOLED(display,0,0,"Select /sd folder")
            print("Select folder")
            for screenLineNum in range (0,7):
                currentFolderLine = ((screenNum*6)+screenLineNum)
                if currentFolderLine < foldersCount:
                    printToOLED(display,2,screenLineNum,listOfFolders[currentFolderLine][3:18])
                    print(listOfFolders[currentFolderLine])
            print("Next")
            printToOLED(display,0,activeLine,">>")
            printToOLED(display,0,7,"Next folder")
            displayOLED()
            x = waitPB()
            if x == MyMenu_DOWN:
                activeLine += 1
            elif x == MyMenu_UP:
                activeLine -= 1
            elif x == MyMenu_SELECT and (activeLine < 7):
                print("selected",listOfFolders[((screenNum*6)+activeLine)])
                return(listOfFolders[((screenNum*6)+activeLine)])
            elif x == MyMenu_SELECT and (activeLine == 7):
                selectNext = True
    assert False,"stop here 1"
   
def selectFile():
    global dirFileNames
    filesCount = len(dirFileNames)
    print("(selectFile): Files count", filesCount)
    print("Files ")
    print(dirFileNames)
    screenCount = int((filesCount+5)/6)
    print("screenCount",screenCount)
    for screenNum in range(0,screenCount):
        activeLine = 1
        selectNext = False
        while not selectNext:
            clearDisplay(display)
            printToOLED(display,0,0,"Select file")
            print("Select file")
            for screenLineNum in range (1,7):
                currentFileLine = ((screenNum*6)+screenLineNum)
                if currentFileLine < filesCount:
                    print(dirFileNames[currentFileLine])
                    printToOLED(display,2,screenLineNum,dirFileNames[currentFileLine][1][:18])
            print("Next")
            printToOLED(display,0,activeLine,">>")
            printToOLED(display,0,7,"Next files")
            displayOLED()
            x = waitPB()
            if x == MyMenu_DOWN:
                activeLine += 1
            elif x == MyMenu_UP:
                activeLine -= 1
            elif x == MyMenu_SELECT and (activeLine < 7):
                print("selected",dirFileNames[((screenNum*6)+activeLine)])
                return(dirFileNames[((screenNum*6)+activeLine)])
            elif x == MyMenu_SELECT and (activeLine == 7):
                selectNext = True
    assert False,"stop here 2"    
    
# Use the board's primary SPI bus
spi = board.SPI()
SD_CS = board.D3
sdcard = sdcardio.SDCard(spi, SD_CS)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
i2cAddrsFound = scanI2C()
i2cAddr_MCP23008 = findMCPI2CAddr(i2cAddrsFound)

initI2CIO8()

listOfFolders = []
getListOfFolders("/sd")
selectedPath = selectFolder()
print("selectedPath",selectedPath)
#assert False,"stop here"

dirFileNames = []
print_directory(selectedPath)
#print("Files on filesystem:")
#print("====================")
#print("dirFileNames",dirFileNames)
filesCount = len(dirFileNames)
print("Files count =",filesCount)
print("Files")
lineCount = 0

for pathFileName in dirFileNames:
    if pathFileName[0] != '/sd/System Volume Information':
        print(pathFileName)
selectedPathFile = selectFile()
print("selectedPathFile",selectedPathFile)