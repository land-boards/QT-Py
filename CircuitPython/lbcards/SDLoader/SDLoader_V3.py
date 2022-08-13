# SDLoader_V3.py
# SD card with MyMenu card
# Read/write SD card and transfer to/from Serial interface
# Runs on RP2040
# Runs under CircuitPython 7.x
#
# Cards (Required)
# http://land-boards.com/blwiki/index.php?title=QTPy49-01#Seeed_Studio_XIAO_RP2040
# http://land-boards.com/blwiki/index.php?title=QTPy49-01
# http://land-boards.com/blwiki/index.php?title=MyMenu
#
# Cards (Optional)
# http://land-boards.com/blwiki/index.php?title=DCE
# http://land-boards.com/blwiki/index.php?title=DTE
# http://land-boards.com/blwiki/index.php?title=SD_Loader#5V_Level_Shifter_.28Optional.29
# http://land-boards.com/blwiki/index.php?title=Mini360_Adapter_Board
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

# MyMenu card defines
# MCP23008 internal register offsets
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
# Pushbutton switch defines
MyMenu_SELECT_BIT = const(0x01)
MyMenu_RIGHT_BIT = const(0x02)
MyMenu_DOWN_BIT = const(0x04)
MyMenu_UP_BIT = const(0x08)
MyMenu_LEFT_BIT = const(0x10)
# Pushbutton switch keypress code return values
MyMenu_NONE = const(0x00)
MyMenu_SELECT = const(0x01)
MyMenu_RIGHT = const(0x02)
MyMenu_DOWN = const(0x03)
MyMenu_UP = const(0x04)
MyMenu_LEFT = const(0x05)

# COM port configuration
baudUnconfig = const(0x00)
baud300 = const(0x01)
baud1200 = const(0x02)
baud9600 = const(0x03)
baud38400 = const(0x04)
baud57600 = const(0x05)
baud115200 = const(0x06)
baudRate = baud9600

straightSerial = const(0x01)
xmodemProtocol = const(0x02)
srecordProtocol = const(0x03)
serProtocol = straightSerial

NoHandshake = const(0x00)
HWHandshake = const(0x01)
XONXOFFHandshake = const(0x02)
EchoHandshake = const(0x03)
handShake = NoHandshake

# MyMenu code follows

# Write to value (val) to MCP23XXX internal register (reg)
def writeMCP23xxxReg(reg, val):
    global i2cAddr_MCP23008
    passVal = bytearray([reg, val])
    while not i2c.try_lock(): # Bound I2C access with lock
        pass
    i2c.writeto(i2cAddr_MCP23008, passVal)
    i2c.unlock()

# read value of MCP23XXX internal register (reg)
def readMCP23xxxReg(reg):
    global i2cAddr_MCP23008
    result = bytearray(1)
    while not i2c.try_lock(): # Bound I2C access with lock
        pass
    i2c.writeto_then_readfrom(i2cAddr_MCP23008, bytes([reg]), result)
    i2c.unlock()
    return result

# Blocking read of the Pushbuttons on the MyMenu card
def waitPB():
    PBs = MyMenu_NONE
    while PBs == MyMenu_NONE:
        PBs = pollPBVals()
        time.sleep(0.01)  # Debounce the switch
    while pollPBVals() != MyMenu_NONE:  # Wait for key release
        pass
    return PBs

# Non blocking read (poll) of the pushbuttons on MyMenu card
# Returns keypress code
def pollPBVals():
    pbVals = readPBs()
    if pbVals == 0:
        return MyMenu_NONE
    elif (pbVals & MyMenu_SELECT_BIT) == MyMenu_SELECT_BIT:
        return MyMenu_SELECT
    elif (pbVals & MyMenu_RIGHT_BIT) == MyMenu_RIGHT_BIT:
        return MyMenu_RIGHT
    elif (pbVals & MyMenu_DOWN_BIT) == MyMenu_DOWN_BIT:
        return MyMenu_DOWN
    elif (pbVals & MyMenu_UP_BIT) == MyMenu_UP_BIT:
        return MyMenu_UP
    elif (pbVals & MyMenu_LEFT_BIT) == MyMenu_LEFT_BIT:
        return MyMenu_LEFT
    return MyMenu_NONE

# Non-blocking read of pushbuttons
# Returns button values as 5 bit value
def readPBs():
    rdVal = (int(readMCP23xxxReg(MCP23008_GPIO)[0]) >> 3) & 0x1F
    return rdVal

# Write to the on-board LEDs
def writeLEDs(wrVal):
    writeMCP23xxxReg(MCP23008_OLAT, wrVal&0x07)

# Initialize the MCP23008
# Upper 5 bits are pushubuttons (inputs)
# Bottom 3 bits are LES (outputs)
def initI2CIO8():
    writeMCP23xxxReg(MCP23008_IODIR, 0xF8)
    writeMCP23xxxReg(MCP23008_IPOL, 0xF8)
    writeMCP23xxxReg(MCP23008_GPINTEN, 0xF8)
    writeMCP23xxxReg(MCP23008_INTCON, 0x00)
    writeMCP23xxxReg(MCP23008_IOCON, 0x22)
    writeMCP23xxxReg(MCP23008_GPPU, 0x00)
    writeMCP23xxxReg(MCP23008_OLAT, 0x00)
    readMCP23xxxReg(MCP23008_GPIO)

# OLED display functions
# call clearOLED() before first writes
# repeat print string (testStr) to the display at xCell, yCell
# call updateOLEDDisplay() to display on acreen

# Clear the OLED screen
def clearOLED(display):
    display.fill(0)

# print string (testStr) to the display at xCell, yCell
# call clearOLED() before first writes
# call updateOLEDDisplay() to display on acreen
def printToOLED(display,xCell,yCell,testStr):
    try:
        display.text(testStr, xCell*5, yCell<<3, 1)
    except FileNotFoundError:
        print(
            "To test the framebuf font setup, you'll need the font5x8.bin file from "
            + "https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/"
            + " in the same directory as this script"
        )

# updateOLEDDisplay() to display on screen
def updateOLEDDisplay():
    try:
        display.show()
    except FileNotFoundError:
        print(
            "To test the framebuf font setup, you'll need the font5x8.bin file from "
            + "https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/"
            + " in the same directory as this script"
        )

# scanI2C() Scan the I2C bus
# Returns a list of all of the I2C devices found
def scanI2C():
    # Auto-detect 
    while not i2c.try_lock():
        pass
    i2cAddrsFound = i2c.scan()
    i2c.unlock()
    return i2cAddrsFound

# findFirstMCPI2CAddr(listOfI2CDevices)
# Pass in the list of I2C Devices from scanI2C()
# Return the first MCP23XXX address found
def findFirstMCPI2CAddr(foundI2CDevices):
    for checkAddr in range(0x20,0x28):
        if checkAddr in foundI2CDevices:
            return(checkAddr)

# SD card code
def writeFile():
    with open("/sd/test.txt", "w") as f:
        f.write("Hello world!\r\n")

# readPrintFileLines() Dump file to USB serial
def readPrintFileLines(pathFileName):
    global uart
    with open(pathFileName, "r") as f:
        for line in f:
            if serialDebug:
                print(line, end='')
            uart.write(bytes(line, 'utf-8'))
            uart.write(bytes('\r', 'utf-8'))

# getListOfFolders - recursively got all paths and put into listOfFolders list
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

# readDirToFilesList - Read in the fileas in directory to dirFileNames
# Can recursively read in directories from the starting path (path)
# Not used recursively in this application
def readDirToFilesList(path, tabs=0):
    global dirFileNames
    dirFileNames=[]
    if serialDebug:
        print("readDirToFilesList: starting path",path)
    for file in os.listdir(path):
        dirFileNames.append((path,file))
        stats = os.stat(path + "/" + file)
        isdir = stats[0] & 0x4000
        # recursively grab directory contents
        if isdir:
            readDirToFilesList(path + "/" + file, tabs + 1)

# selectFolder() - Select the folder and return the path to the selected folder
# Easiest structure is to have separate folders for about 32 files per folder
# so there's less files per folder to step through
def selectFolder():
    global listOfFolders
    foldersCount = len(listOfFolders)
    screenCount = int((foldersCount+5)/6)
    for screenNum in range(0,screenCount):
        currentSelectedLine = 1
        selectNext = False
        while not selectNext:
            clearOLED(display)
            if serialDebug:
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

# selectFile() - select a particular file
# Folder was previously selected
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
            if pbVal == MyMenu_DOWN and currentSelectedLine < 7:
                currentSelectedLine += 1
            elif pbVal == MyMenu_UP and currentSelectedLine > 0:
                currentSelectedLine -= 1
            elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine < 7):
                return(dirFileNames[((screenNum*6)+currentSelectedLine)])
            elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 7):
                selectNext = True
    assert False,"stop here 2"    

# configSerialCOM() - Configure the serial communications
# baud rate, protocol, handshake
def configSerialCOM():
    global baudRate
    global serProtocol
    global handShake
    currentSelectedLine = 1
    selectNext = False
    while not selectNext:
        clearOLED(display)
        printToOLED(display,0,0,"Configure Serial")
        printToOLED(display,2,1,"Baud Rate")
        if baudRate == baud300:
            printToOLED(display,13,1," 300")
        elif baudRate == baud1200:
            printToOLED(display,13,1," 1200")
        elif baudRate == baud9600:
            printToOLED(display,13,1," 9600")
        elif baudRate == baud38400:
            printToOLED(display,13,1," 38.4k")
        elif baudRate == baud57600:
            printToOLED(display,13,1," 57.6k")
        elif baudRate == baud115200:
            printToOLED(display,13,1," 115.2k")
        elif baudRate == baudUnconfig:
            printToOLED(display,13,1," None")
        printToOLED(display,2,2,"Protocol")
        if serProtocol == straightSerial:
            printToOLED(display,11,2," Serial")
        elif serProtocol == xmodemProtocol:
            printToOLED(display,11,2," xmodem")
        elif serProtocol == srecordProtocol:
            printToOLED(display,11,2," s-record")
        printToOLED(display,2,3,"Handshake")
        if handShake == NoHandshake:
            printToOLED(display,13,3," None")
        elif handShake == HWHandshake:
            printToOLED(display,13,3," RTS/CTS")
        elif handShake == XONXOFFHandshake:
            printToOLED(display,13,3," XON/XOFF")
        elif handShake == EchoHandshake:
            printToOLED(display,13,3," Echoed")
        printToOLED(display,2,4,"Exit")
        printToOLED(display,0,currentSelectedLine,">")
        updateOLEDDisplay()
        pbVal = waitPB()
        if pbVal == MyMenu_DOWN and currentSelectedLine < 4:
            currentSelectedLine += 1
        elif pbVal == MyMenu_UP and currentSelectedLine > 1:
            currentSelectedLine -= 1
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 1):
            setBaudrate()
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 2):
            configProtocol()
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 3):
            configHandshake()
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 4):
            storeConfig()
            return

# setBaudrate() - Sub-menu to set the baud rate
# Called from configSerialCOM()
def setBaudrate():
    global baudRate
    currentSelectedLine = 1
    while True:
        clearOLED(display)
        printToOLED(display,0,0,"Set Baud Rate")
        printToOLED(display,2,1,"300")
        printToOLED(display,2,2,"1200")
        printToOLED(display,2,3,"9600")
        printToOLED(display,2,4,"38,400")
        printToOLED(display,2,5,"57,600")
        printToOLED(display,2,6,"115,200")
        printToOLED(display,2,7,"Exit")
        printToOLED(display,0,currentSelectedLine,">")
        updateOLEDDisplay()
        pbVal = waitPB()
        if pbVal == MyMenu_DOWN and currentSelectedLine < 7:
            currentSelectedLine += 1
        elif pbVal == MyMenu_UP and currentSelectedLine > 1:
            currentSelectedLine -= 1
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 1):
            baudRate = baud300
            setUARTConfig()
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 2):
            baudRate = baud1200
            setUARTConfig()
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 3):
            baudRate = baud9600
            setUARTConfig()
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 4):
            baudRate = baud38400
            setUARTConfig()
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 5):
            baudRate = baud57600
            setUARTConfig()
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 6):
            baudRate = baud115200
            setUARTConfig()
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 7):
            return
   
# configProtocol() - Sub-menu to set the protocol type
# Called from configSerialCOM()
def configProtocol():
    global serProtocol
    currentSelectedLine = 1
    while True:
        clearOLED(display)
        printToOLED(display,0,0,"Set Protocol")
        printToOLED(display,2,1,"Serial")
        printToOLED(display,2,2,"XMODEM")
        printToOLED(display,2,3,"s-record")
        printToOLED(display,2,4,"Exit")
        printToOLED(display,0,currentSelectedLine,">")
        updateOLEDDisplay()
        pbVal = waitPB()
        if pbVal == MyMenu_DOWN and currentSelectedLine < 4:
            currentSelectedLine += 1
        elif pbVal == MyMenu_UP and currentSelectedLine > 1:
            currentSelectedLine -= 1
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 1):
            serProtocol = straightSerial
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 2):
            serProtocol = xmodemProtocol
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 3):
            serProtocol = srecordProtocol
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 4):
            return
    
# configHandshake() - Sub-menu to set the handshake type
# Called from configSerialCOM()
def configHandshake():
    global handShake
    currentSelectedLine = 1
    while True:
        clearOLED(display)
        printToOLED(display,0,0,"Set Handshake")
        printToOLED(display,2,1,"None")
        printToOLED(display,2,2,"RTS/CTS")
        printToOLED(display,2,3,"XON/XOFF")
        printToOLED(display,2,4,"Wait foe echo")
        printToOLED(display,2,5,"Exit")
        printToOLED(display,0,currentSelectedLine,">")
        updateOLEDDisplay()
        pbVal = waitPB()
        if pbVal == MyMenu_DOWN and currentSelectedLine < 5:
            currentSelectedLine += 1
        elif pbVal == MyMenu_UP and currentSelectedLine > 1:
            currentSelectedLine -= 1
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 1):
            handShake = NoHandshake
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 2):
            handShake = HWHandshake
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 3):
            handShake = XONXOFFHandshake
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 4):
            handShake = EchoHandshake
            return
        elif (pbVal == MyMenu_SELECT or pbVal == MyMenu_RIGHT) and (currentSelectedLine == 5):
            handShake = NoHandshake
            return

# findFile() - Find a file
# First select the folder
# Then select the file
def findFile():
    getListOfFolders("/sd")
    selectedPath = []
    selectedPathFile = []
    selectedPath = selectFolder()
    if serialDebug:
        print("findFile: selectedPath", selectedPath)
    readDirToFilesList(selectedPath)
    filesCount = len(dirFileNames)
    lineCount = 0
    selectedPathFile = selectFile()
    return selectedPathFile

# errorMessage(errorMsg) to USB serial and OLED
# Wait for button press to continue
def errorMessage(errorMsg):
    if serialDebug:
        print(errorMsg)
    clearOLED(display)
    printToOLED(display,0,0,errorMsg)
    printToOLED(display,0,2,"Press button to continue")
    updateOLEDDisplay()
    waitPB()

def setUARTConfig():
    global uart
    global uartInit
    if serialDebug:
        if uartInit:
            print("setUARTConfig: UART was initialized")
        else:
            print("setUARTConfig: UART was not initialized")
    if uartInit:
        uart.deinit()
    if baudRate == baud300:
        uart = busio.UART(board.TX, board.RX, baudrate=300)
    elif baudRate == baud1200:
        uart = busio.UART(board.TX, board.RX, baudrate=1200)
    elif baudRate == baud9600:
        uart = busio.UART(board.TX, board.RX, baudrate=9600)
    elif baudRate == baud38400:
        uart = busio.UART(board.TX, board.RX, baudrate=38400)
    elif baudRate == baud57600:
        uart = busio.UART(board.TX, board.RX, baudrate=57600)
    elif baudRate == baud115200:
        uart = busio.UART(board.TX, board.RX, baudrate=115200)
    else:
        uart = busio.UART(board.TX, board.RX, baudrate=9600)
    if serialDebug:
        print("setUARTConfig: set uartInit")
    uartInit = True
    return

# uploadSerial() - Upload the selected file on the serial port
def uploadSerial():
    global selectedFile
    pathFileName = selectedFile[0] + selectedFile[1]
    if serialDebug:
        print("uploadSerial(): listing file",pathFileName)
    # Make sure file was selected first
    if pathFileName == '':
        errorMessage("Select file first")
        return
    # Make sure baud rate was selected
    if baudRate == baudUnconfig:
        errorMessage("Config baud rate!")
        return
    clearOLED(display)
    printToOLED(display,0,0,"Uploading Serial")
    printToOLED(display,0,1,pathFileName)
    updateOLEDDisplay()
    readPrintFileLines(pathFileName)
    printToOLED(display,0,2,"Upload is Done!")
    updateOLEDDisplay()
    time.sleep(2)
    return

# receiveSerial()
def receiveSerial():
    if pathFileName == '':
        errorMessage("Select file first")
        return
    # Make sure baud rate was selected
    if baudRate == baudUnconfig:
        errorMessage("Config baud rate!")
        return
    clearOLED(display)
    printToOLED(display,0,0,"Receiving Serial")
    updateOLEDDisplay()
    time.sleep(2)
    return
    
# Top Level Menu code
def topMenu():
    global selectedFile
    global uart
    global uartInit
#     setUARTConfig()
    loopMenu = True
    currentSelectedLine = 1
    while loopMenu:
        clearOLED(display)
        printToOLED(display,0,0,"SDLoader V3")
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
                if serialDebug:
                    print("main(): selectedFile",selectedFile)
            if currentSelectedLine == 2:
                uploadSerial()
            if currentSelectedLine == 3:
                receiveSerial()
            if currentSelectedLine == 4:
                configSerialCOM()
            if currentSelectedLine == 5:
                clearOLED(display)
                updateOLEDDisplay()
                break

# initConfig() - Initialize the configuration parameter values
def initConfig():
    global baudRate
    global serProtocol
    global handShake
    if serialDebug:
        print("initConfig: Got here")
    baudRate = baud9600
    serProtocol = straightSerial
    handShake = NoHandshake
    if serialDebug:
        print("initConfig: Storing initial values")
    storeConfig()
    if serialDebug:
        print("initConfig: Stored")
    return

# loadConfig() - Load the configuration parameters from the SD card
def loadConfig():
    global baudRate
    global serProtocol
    global handShake
    try:
        with open('/sd/SDLdr.cfg', 'r') as fp:
            comCfg = fp.read()
            cfgList = comCfg.split(',')
            baudRate = int(cfgList[0])
            if serialDebug:
                print("loadConfig: baudRate",baudRate)
            serProtocol = int(cfgList[1])
            if serialDebug:
                print("loadConfig: serProtocol",serProtocol)
            handShake = int(cfgList[2])
            if serialDebug:
                print("loadConfig: handShake",handShake)
    except OSError as e:  # Typically when the filesystem isn't writeable...
        assert False,"loadConfig: file read error"
    setUARTConfig()
    return
    
# storeConfig() - Store the configuration parameters to the SD card
def storeConfig():
    global baudRate
    global serProtocol
    global handShake
    if serialDebug:
        print("storeConfig: Got here")
    try:
        with open('/sd/SDLdr.cfg', 'w') as fp:
            fp.write(str(baudRate) + ',' + str(serProtocol) + ',' + str(handShake))
            fp.flush()
    except OSError as e:  # Typically when the filesystem isn't writeable...
        assert False,"storeConfig: file write error"
    return
    
serialDebug = False

# Use the board's primary SPI bus
spi = board.SPI()
SD_CS = board.D0
sdcard = sdcardio.SDCard(spi, SD_CS)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
i2cAddrsFound = scanI2C()
i2cAddr_MCP23008 = findFirstMCPI2CAddr(i2cAddrsFound)

initI2CIO8()
uartInit = False

osList = os.listdir('/sd')
if serialDebug:
    print("main: osList",osList)
if 'SDLdr.cfg' not in osList:
    if serialDebug:
        print('main: No SDLoader_cfg.txt file')
    initConfig()
else:
    if serialDebug:
        print("main: SDLdr.cfg found")
    loadConfig()
    
listOfFolders = []
dirFileNames = []
selectedFile = ('','')

topMenu()
