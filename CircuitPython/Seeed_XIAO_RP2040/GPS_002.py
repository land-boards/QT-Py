# GPS_001.py
# Communicate with a NEO-7M GPS module
# Read/print serial data
# Runs on XIAO RP2040 board
# http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)
# On QTPy49 card
# http://land-boards.com/blwiki/index.php?title=QTPy49
# 
# Based on
# https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial
#
# Docs
# https://docs.circuitpython.org/projects/gps/en/latest/api.html#implementation-notes
# https://docs.circuitpython.org/projects/gps/en/latest/
# https://github.com/adafruit/Adafruit_CircuitPython_GPS
# 
# Wiring
# Signal   Color  From          To
# GND      Black  QTPy49 J4-1   GPS pin 4
# VCC      Red    QTPy49 J4-2   GPS pin 5
# QTPy>GPS Blue   QTPy49 J4-3   GPS pin 2
# GPS>QTPy White  QTPy49 J4-4   GPS pin 3
# GND      Black  QTPy49 J5-1   PulseGen GND
# VCC      Red    QTPy49 J5-2   PulseGen VCC
# PPS      Purple GPU pin 1     PulseGen In

import board
import busio
import digitalio
import time
import gc

uart = busio.UART(board.TX, board.RX, baudrate=9600)

print("GPS002.py")
print("Free space",gc.mem_free())
while True:
    serData = uart.read(32)
    if serData is not None:
        data_string = ''.join([chr(b) for b in serData])
        print(data_string, end="")
        # print("\nFree space",gc.mem_free())
