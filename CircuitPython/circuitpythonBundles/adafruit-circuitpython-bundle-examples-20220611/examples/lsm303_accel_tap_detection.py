# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import adafruit_lsm303_accel

i2c = board.I2C()  # uses board.SCL and board.SDA
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
accel.range = adafruit_lsm303_accel.Range.RANGE_8G
accel.set_tap(1, 30)

while True:
    if accel.tapped:
        print("Tapped!\n")
