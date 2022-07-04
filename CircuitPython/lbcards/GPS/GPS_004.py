# GPS_004.py
# https://github.com/land-boards/QT-Py/blob/main/CircuitPython/Seeed_XIAO_RP2040/GPS_004.py
# Tool to create bytestrings
# https://github.com/land-boards/lb-Arduino-Code/tree/master/LBCards/GPSFreqStd/FreqStdCap
# Save as code.py to make it auto-run
# Communicate with a NEO-7M GPS module
# On QTPy49 card
# http://land-boards.com/blwiki/index.php?title=QTPy49
# Runs on Adafruit QT Py or XIAO SAMD21 or RP2040 boards
# http://land-boards.com/blwiki/index.php?title=QT_Py_(SAMD_based)
# 
# Based on
# https://learn.adafruit.com/circuitpython-essentials/circuitpython-uart-serial
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
# 
# Capture of data from GPS after sync
# $GPGLL,4000.43027,N,07935.34703,W,115133.00,A,A*72
# $GPRMC,115134.00,A,4000.43027,N,07935.34678,W,0.207,,260622,,,A*66
# $GPVTG,,T,,M,0.207,N,0.384,K,A*29
# 00000000001111111111222222222233333333334444444444555555555566666666667777777777
# 01234567890123456789012345678901234567890123456789012345678901234567890123456789
# $GPGGA,115134.00,4100.43027,N,07835.34678,W,1,07,1.25,288.9,M,-34.0,M,,*6D
#        hhmmss.ss,lat       ,N,long       ,W,Q,NS
# $GPGSA,A,3,27,13,08,30,07,14,17,,,,,,1.91,1.25,1.45*05
# $GPGSV,4,1,13,01,44,141,17,07,68,189,22,08,43,048,23,13,16,310,29*7A
# $GPGSV,4,2,13,14,41,299,28,17,25,235,31,19,00,231,,21,51,091,*75
# $GPGSV,4,3,13,27,06,052,16,28,20,288,,30,66,282,36,46,22,241,*7E
# $GPGSV,4,4,13,48,25,238,*49

import board
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import time
import gc

uart = busio.UART(board.TX, board.RX, baudrate=9600)

# Created byte strings for typical values
# Created using utility running on Arduino
# https://github.com/land-boards/lb-Arduino-Code/tree/master/LBCards/GPSFreqStd/FreqStdCap
 
# 10 MHz output
bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x80\x96\x98\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x59\x13'

# 8 MHz output
# bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x00\x12\x7A\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x37\x2B'

# 1 MHz output
# bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x40\x42\x0F\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x3C\x35'

freqSet = False
# print("GPS004.py")
# print("Free space",gc.mem_free())

led = DigitalInOut(board.D0)
led.direction = Direction.OUTPUT
led.value = True
time.sleep(1)
led.value = False

serByteString = b''
ledCount = 0
while True:
    serVal = uart.read(1)
    if not freqSet and ledCount > 50:
        ledCount = 0
        led.value = not led.value
    ledCount += 1
    if serVal is not None:
        serByteString += serVal        
        if chr(serVal[0]) == '\n':
            data_string = ''.join([chr(b) for b in serByteString])
            if 'GPGGA' in data_string:
                #print(data_string, end="")
                if len(data_string) > 48:
                    if data_string[45] == ',' and data_string[48] == ',':
                        # print("sats str",data_string[46:48])
                        numSats=int(data_string[46:48])
                        if numSats == 0:
                            freqSet = False
                        elif not freqSet and numSats > 0:
#                             print("Num Sats",numSats)
#                             print(data_string, end="")
                            uart.write(bytStr)
                            freqSet = True
                            led.value = True
            serByteString = b''
