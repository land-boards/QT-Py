# SDCard_ListDir.py
# SD card example code
# Runs under CircuitPython 7.x

import board
import busio
import sdcardio
import storage
import os

# Use the board's primary SPI bus
spi = board.SPI()

SD_CS = board.D3

sdcard = sdcardio.SDCard(spi, SD_CS)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

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

def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)


print("Files on filesystem:")
print("====================")
print_directory("/sd")

