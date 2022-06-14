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

def waitPB():
    PBs = MyMenu_NONE
    while PBs == MyMenu_NONE:
        PBs = pollPBVals()
        time.sleep(0.01)
    while pollPBVals() != MyMenu_NONE:
        pass
    return PBs

def pollPBVals():
    kbVal = readPBs()
    if kbVal == 0:
        return MyMenu_NONE
    elif (kbVal & MyMenu_SELECT_BIT) == MyMenu_SELECT_BIT:
        return MyMenu_SELECT
    elif (kbVal & MyMenu_RIGHT_BIT) == MyMenu_RIGHT_BIT:
        return MyMenu_RIGHT
    elif (kbVal & MyMenu_DOWN_BIT) == MyMenu_DOWN_BIT:
        return MyMenu_DOWN
    elif (kbVal & MyMenu_UP_BIT) == MyMenu_UP_BIT:
        return MyMenu_UP
    elif (kbVal & MyMenu_LEFT_BIT) == MyMenu_LEFT_BIT:
        return MyMenu_LEFT
    return MyMenu_NONE

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

def clearOLED(display):
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

def updateOLEDDisplay():
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

def readPrintFileLines(pathFileName):
    with open(pathFileName, "r") as f:
        print("Printing lines in file:")
        line = f.readline()
        for line in f:
            print(line, end='')

# getListOfFolders - recursively got all paths
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

# readDirectoryToList - Read in the directory to listOfFolders
def readDirectoryToList(path, tabs=0):
    global dirFileNames
    global listOfFolders
    if path not in listOfFolders:
        listOfFolders.append(path)
    for file in os.listdir(path):
        dirFileNames.append((path,file))
        stats = os.stat(path + "/" + file)
        isdir = stats[0] & 0x4000
        # recursively grab directory contents
        if isdir:
            readDirectoryToList(path + "/" + file, tabs + 1)

# selectFolder() - Select the folder and return the path to the selected folder
def selectFolder():
    global listOfFolders
    foldersCount = len(listOfFolders)
    screenCount = int((foldersCount+5)/6)
    for screenNum in range(0,screenCount):
        currentSelectedLine = 1
        selectNext = False
        while not selectNext:
            clearOLED(display)
            printToOLED(display,0,0,"Select /sd folder")
            for screenLineNum in range (0,7):
                currentFolderLine = ((screenNum*6)+screenLineNum)
                if currentFolderLine < foldersCount:
                    printToOLED(display,2,screenLineNum,listOfFolders[currentFolderLine][3:18])
            printToOLED(display,0,currentSelectedLine,">")
            printToOLED(display,2,7,"Next folder")
            updateOLEDDisplay()
            pbVal = waitPB()
            if pbVal == MyMenu_DOWN:
                currentSelectedLine += 1
            elif pbVal == MyMenu_UP:
                currentSelectedLine -= 1
            elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine < 7):
                return(listOfFolders[((screenNum*6)+currentSelectedLine)])
            elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 7):
                selectNext = True
    assert False,"stop here 1"
   
def selectFile():
    global dirFileNames
    filesCount = len(dirFileNames)
    screenCount = int((filesCount+5)/6)
    for screenNum in range(0,screenCount):
        currentSelectedLine = 1
        selectNext = False
        while not selectNext:
            clearOLED(display)
            printToOLED(display,0,0,"Select file")
            for screenLineNum in range (1,7):
                currentFileLine = ((screenNum*6)+screenLineNum)
                if currentFileLine < filesCount:
                    printToOLED(display,2,screenLineNum,dirFileNames[currentFileLine][1][:18])
            printToOLED(display,0,currentSelectedLine,">")
            printToOLED(display,2,7,"Next files")
            updateOLEDDisplay()
            pbVal = waitPB()
            if pbVal == MyMenu_DOWN:
                currentSelectedLine += 1
            elif pbVal == MyMenu_UP:
                currentSelectedLine -= 1
            elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine < 7):
                return(dirFileNames[((screenNum*6)+currentSelectedLine)])
            elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 7):
                selectNext = True
    assert False,"stop here 2"    
    
def findFile():
    getListOfFolders("/sd")
    selectedPath = selectFolder()
    readDirectoryToList(selectedPath)
    filesCount = len(dirFileNames)
    lineCount = 0
    selectedPathFile = selectFile()
    return selectedPathFile

def uploadSerial():
    global selectedFile
    clearOLED(display)
    printToOLED(display,0,0,"Uploading Serial")
    updateOLEDDisplay()
    pathFileName = selectedFile[0] + selectedFile[1]
    print("listing file",pathFileName)
    readPrintFileLines(pathFileName)
    time.sleep(2)
    return

def receiveSerial():
    clearOLED(display)
    printToOLED(display,0,0,"Receiving Serial")
    updateOLEDDisplay()
    time.sleep(2)
    return
    
def configCOM():
    clearOLED(display)
    printToOLED(display,0,0,"Config Serial")
    updateOLEDDisplay()
    time.sleep(2)
    return

def topMenu():
    global selectedFile
    loopMenu = True
    currentSelectedLine = 1
    while loopMenu:
        clearOLED(display)
        printToOLED(display,0,0,"SDLoader V2")
        printToOLED(display,2,1,"Select file")
        printToOLED(display,2,2,"Send file to Ser.")
        printToOLED(display,2,3,"Rcv file from Ser.")
        printToOLED(display,2,4,"COM port config")
        printToOLED(display,2,5,"Exit")
        if selectedFile == ('',''):
            printToOLED(display,0,7,"No file selected")
        else:
            printToOLED(display,0,7,selectedFile[1][:20])
        printToOLED(display,0,currentSelectedLine,">")
        updateOLEDDisplay()
        pbVal = waitPB()
        if pbVal == MyMenu_DOWN and currentSelectedLine < 5:
            currentSelectedLine += 1
        elif pbVal == MyMenu_UP and currentSelectedLine > 1:
            currentSelectedLine -= 1
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT):
            if currentSelectedLine == 1:
                selectedFile = findFile()
                print("main(): selectedFile",selectedFile)
            if currentSelectedLine == 2:
                uploadSerial()
            if currentSelectedLine == 3:
                receiveSerial()
            if currentSelectedLine == 4:
                configCOM()
            if currentSelectedLine == 5:
                clearOLED(display)
                updateOLEDDisplay()
                break

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
dirFileNames = []
selectedFile = ('','')

topMenu()

