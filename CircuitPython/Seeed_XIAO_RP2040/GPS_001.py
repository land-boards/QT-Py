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

while True:
# Make sure to call gps.update() every loop iteration and at least twice
# as fast as data comes from the GPS unit (usually every second).
# This returns a bool that's true if it parsed new data (you can ignore it
# though if you don't care and instead look at the has_fix property).
    if not gps.update() or not gps.has_fix:
        time.sleep(0.1)
        print("Waiting",lc)
        lc += 1
        continue

#     time.sleep(0.25)
    print("Not waiting")
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



# namespace
# {
#   struct GPS_TP5_MSG
#   {
#     uint8_t   header1;
#     uint8_t   header2;
#     uint8_t   message_class;
#     uint8_t   message_id;
#     uint16_t  length;
#     uint8_t   timepulse_idx;
#     uint8_t   version;
#     uint16_t  reserved;
#     int16_t   antenna_cable_delay;
#     int16_t   rf_group_delay;
#     uint32_t  frequency_unlocked;
#     uint32_t  frequency_locked;
#     uint32_t  duty_cycle_unlocked;
#     uint32_t  duty_cycle_locked;
#     uint32_t  user_delay;
#     uint32_t  flags;
#     uint16_t  checksum;
#   } __attribute__((packed));
# 
#   const uint16_t GPS_TP5_ACTIVE           = 0x01;
#   const uint16_t GPS_TP5_SYNC_TO_GNSS     = 0x02;
#   const uint16_t GPS_TP5_LOCKED_OTHER_SET = 0x04;
#   const uint16_t GPS_TP5_IS_FREQUENCY     = 0x08;
#   const uint16_t GPS_TP5_IS_LENGTH        = 0x10;
#   const uint16_t GPS_TP5_ALIGN_TO_TOW     = 0x20;
#   const uint16_t GPS_TP5_POLARITY_RISING  = 0x40;
# 
#   const uint32_t GPS_TP5_DUTY_CYCLE_50    = 0x80000000;
#   
#   uint16_t calculateChecksum(uint8_t *p, size_t len)
#   {
#     uint8_t ck_a = 0;
#     uint8_t ck_b = 0;
#     while (len--)
#     {
#       ck_a = ck_a + *p++;
#       ck_b = ck_b + ck_a;
#     }
#     return ck_a | (ck_b << 8);
#   }
# }