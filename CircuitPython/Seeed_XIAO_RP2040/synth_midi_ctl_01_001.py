# synth_midi_ctl_01_001.py

"""
Example for XIAO SAM and RP2040 boards.
Blinks the gate aqnd clk lines.
"""

import time
import board
import digitalio
 
gate = digitalio.DigitalInOut(board.D3)
gate.direction = digitalio.Direction.OUTPUT
clk = digitalio.DigitalInOut(board.D4)
clk.direction = digitalio.Direction.OUTPUT
 
while True:
    gate.value = False    # high to turn off
    time.sleep(0.5)
    gate.value = True   # low to turn on
    time.sleep(0.5)
    clk.value = False    # high to turn off
    time.sleep(1.5)
    clk.value = True    # high to turn off
    time.sleep(1.5)
