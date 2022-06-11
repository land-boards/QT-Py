# SPDX-FileCopyrightText: Copyright (c) 2019-2021 Gaston Williams
#
# SPDX-License-Identifier: Unlicense

#  This is example is for the SparkFun Qwiic Single Relay.
#  SparkFun sells these at its website: www.sparkfun.com
#  Do you like this library? Help support SparkFun. Buy a board!
#  https://www.sparkfun.com/products/15093

"""
  Qwiic Relay Example 3 - example3_i2c_Scanner.py
  Written by Gaston Williams, June 17th, 2019
  The Qwiic Single Relay is an I2C controlled relay produced by sparkfun

  Example 3 - I2C Scanner
  This progam uses CircuitPython BusIO library to find the current
  address of the Qwiic Relay. It uses information from
  https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/i2c-devices
  to manually scan for the Qwiic Single Relay.

  Since the Qwiic Single Relay responds to any byte read request after it's
  base address is written, i2c.scan()cannot be used.

  This code manually scans addresses from 0x03 to 0x80, using only writes,
  not writes and reads,to find i2c devices.

  The factory default address is 0x18.
"""
import sys
from time import sleep
import board

i2c = board.I2C()

# Since i2c.scan() returns all addresses above the relay address,
# we look for the relay address using only write requests.


def test_i2c_write(addr):
    "Write to an address to see if there's an device there" ""
    while not i2c.try_lock():
        pass

    try:
        # Make an empty write request to an address
        i2c.writeto(addr, b"")
        return True

    except OSError:
        return False

    # Always unlock the i2c bus, before return
    finally:
        i2c.unlock()


print("Press Ctrl-C to exit program")

try:
    while True:
        found = []

        # scan through all possible i2c addresses doi
        for address in range(0x03, 0x80):
            if test_i2c_write(address):
                found.append(address)

        if found:
            print(
                "I2C addresses found:",
                [hex(device_address) for device_address in found],
            )
        else:
            print("No I2C device found.")

        # wait a bit and scan again
        sleep(5)

except KeyboardInterrupt:
    pass
