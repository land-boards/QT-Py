# GPS_003.py
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
# $GPGLL,4000.43027,N,07935.34703,W,115133.00,A,A*72
# $GPRMC,115134.00,A,4000.43027,N,07935.34678,W,0.207,,260622,,,A*66
# $GPVTG,,T,,M,0.207,N,0.384,K,A*29
# $GPGGA,115134.00,4000.43027,N,07935.34678,W,1,07,1.25,288.9,M,-34.0,M,,*6D
# $GPGSA,A,3,27,13,08,30,07,14,17,,,,,,1.91,1.25,1.45*05
# $GPGSV,4,1,13,01,44,141,17,07,68,189,22,08,43,048,23,13,16,310,29*7A
# $GPGSV,4,2,13,14,41,299,28,17,25,235,31,19,00,231,,21,51,091,*75
# $GPGSV,4,3,13,27,06,052,16,28,20,288,,30,66,282,36,46,22,241,*7E
# $GPGSV,4,4,13,48,25,238,*49


import board
import busio
import digitalio
import time
import gc

uart = busio.UART(board.TX, board.RX, baudrate=9600)

print("GPS003.py")
print("Free space",gc.mem_free())
serByteString = b''
while True:
    serVal = uart.read(1)
    if serVal is not None:
        serByteString += serVal        
        if chr(serVal[0]) == '\n':
            data_string = ''.join([chr(b) for b in serByteString])
            print(data_string, end="")
            serByteString = b''
