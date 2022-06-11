# SPDX-FileCopyrightText: Copyright (c) 2019-2021 Gaston Williams
#
# SPDX-License-Identifier: Unlicense

#  This is example is for the SparkFun Qwiic Single Relay.
#  SparkFun sells these at its website: www.sparkfun.com
#  Do you like this library? Help support SparkFun. Buy a board!
#  https://www.sparkfun.com/products/15093

"""
  Qwiic Relay Example 2 - example2_change_i2c_address.py
  Written by Gaston Williams, June 19th, 2019
  Based on Arduino code written by
  Kevin Kuwata @ SparkX, March 21, 2019
  The Qwiic Single Relay is a I2C controlled relay

  Example 2 - Change I2C Address:
  This program uses the Qwiic Relay CircuitPython Library to change
  the I2C address for the device. You enter in the DEC value (8-119) or
  HEX value (0x08-0x77) for the new Relay address.  After the i2c address
  is changed, you can run the example3_i2c_scanner.py program to validate
  the i2c address.

  Syntax: python3 change_i2c_address.py [address]
    where address is an optional current address value in decimal or hex

    The default value for the address is 24 [0x18]
"""

import sys
import board
import sparkfun_qwiicrelay

# The default QwiicRelay i2c address is 0x18 (24)
i2c_address = 0x18

# print('Arguement count: ' , len(sys.argv))
# print('List: ' + str(sys.argv))

# If we were passed an arguement, then use it as the address
if len(sys.argv) > 1:
    try:
        # check to see if hex or decimal arguement
        if "0x" in sys.argv[1]:
            i2c_address = int(sys.argv[1], 16)
        else:
            i2c_address = int(sys.argv[1])
    except ValueError:
        print("Ignoring invalid arguement: " + str(sys.argv[1]))

# Show the initial address
print("Current i2c address = " + str(i2c_address) + " [" + hex(i2c_address) + "]")

# Create busio object using our Board I2C port
i2c = board.I2C()
relay = sparkfun_qwiicrelay.Sparkfun_QwiicRelay(i2c, i2c_address)

if relay.connected:
    print("Qwiic Relay Example.")
else:
    # if we can't connecct, something is wrong so just quit
    print("Relay does not appear to be connected. Please check wiring.")
    sys.exit()

print("Address: " + str(i2c_address) + " [" + hex(i2c_address) + "]")

text = input(
    "Enter a new I2C address (as a decimal from 8 to 119 or hex 0x08 to 0x77):"
)

# check to see if hex or decimal value
if "0x" in text:
    new_address = int(text, 16)
else:
    new_address = int(text)

print("Changing address to " + str(new_address) + " [" + hex(new_address) + "]")

result = relay.set_i2c_address(new_address)

if result:
    print("Address changed to " + str(new_address) + " [" + hex(new_address) + "]")
    # After the change check the new connection and show firmware version
    if relay.connected:
        print("Connected to Relay after address change.")
    else:
        print("Error after address change. Cannot connect to Relay.")

else:
    print("Address change failed.")

# good advice whether the address changed worked or not
print("Run example3_i2c_scanner.py to verify the Qwiic Relay address.")
