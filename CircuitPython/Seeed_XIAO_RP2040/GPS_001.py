# GPS_001.py
# Communicate with a NEO-7M GPS module
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
import adafruit_gps
import time
import gc

def format_dop(dop):
    # https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)
    if dop > 20:
        msg = "Poor"
    elif dop > 10:
        msg = "Fair"
    elif dop > 5:
        msg = "Moderate"
    elif dop > 2:
        msg = "Good"
    elif dop > 1:
        msg = "Excellent"
    else:
        msg = "Ideal"
    return f"{dop} - {msg}"


talkers = {
    "GA": "Galileo",
    "GB": "BeiDou",
    "GI": "NavIC",
    "GL": "GLONASS",
    "GP": "GPS",
    "GQ": "QZSS",
    "GN": "GNSS",
}


# For most CircuitPython boards:
# led = digitalio.DigitalInOut(board.LED)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
# led.direction = digitalio.Direction.OUTPUT

uart = busio.UART(board.TX, board.RX, baudrate=9600)
gps = adafruit_gps.GPS(uart, debug=False)

print("GPS001.py")
gps.send_command(b"PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0")
print("Sent 1st")
time.sleep(1)
gps.send_command(b"PMTK220,1000")
print("Sent 2nd - looping")
print("Free space",gc.mem_free())
lc=0

def setFreqMHz(freqValMHz):
	# CFG-TP5 message found in Section 35.19.4 og Protocol Spec
	# Generated messages using Arduino running
	# 10 MHz output
	# bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x80\x96\x98\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x59\x13'
	# 8 MHz output
	# bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x00\x12\x7A\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x37\x2B'
	# 1 MHz output
	# bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x40\x42\x0F\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x3C\x35'
	if freqValMHz == 10:
		bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x80\x96\x98\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x59\x13'
	elif freqValMHz == 8:
		bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x00\x12\x7A\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x37\x2B'
	elif freqValMHz ==  1:
		bytStr = b'\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x05\x0D\x00\x00\x40\x42\x0F\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x0F\x00\x00\x00\x3C\x35'
	gps.write(bytStr)
	return

freqSet = False

while True:
# Make sure to call gps.update() every loop iteration and at least twice
# as fast as data comes from the GPS unit (usually every second).
# This returns a bool that's true if it parsed new data (you can ignore it
# though if you don't care and instead look at the has_fix property).
    #print("Free space",gc.mem_free())
    if not gps.update() or not gps.has_fix:
        if not gps.has_fix:
			freqSet = False
		else:
			freqSet = True
		time.sleep(0.1)
        gc.collect()
        continue
		
	if not freqSet:
		freqSet = True
		setFreqMHz(10)

    gc.collect()
    if gps.nmea_sentence[3:6] == "GSA":
        print(f"{gps.latitude:.6f}, {gps.longitude:.6f} {gps.altitude_m}m")
        print(f"2D Fix: {gps.has_fix}  3D Fix: {gps.has_3d_fix}")
        print(f"  PDOP (Position Dilution of Precision): {format_dop(gps.pdop)}")
        print(f"  HDOP (Horizontal Dilution of Precision): {format_dop(gps.hdop)}")
        print(f"  VDOP (Vertical Dilution of Precision): {format_dop(gps.vdop)}")
        print("Satellites used for fix:")
        for s in gps.sat_prns:
            talker = talkers[s[0:2]]
            number = s[2:]
            print(f"  {talker}-{number} ", end="")
            if gps.sats is None:
                print("- no info")
            else:
                try:
                    sat = gps.sats[s]
                    if sat is None:
                        print("- no info")
                    else:
                        print(f"Elevation:{sat[1]}* Azimuth:{sat[2]}* SNR:{sat[3]}dB")
                except KeyError:
                    print("- no info")
        print()
