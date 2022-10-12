# synth_midi_ctl_01_001.py

"""
Example for XIAO RP2040 boards.
Blinks the GATE and CLK lines.
Rev 1 card is active Low to set CLK ans GATE pins out.
Adafruit MIDI handler
Starts out with USB MIDI
Use MIDI Editor to send out music over USB
https://midieditor.org/
"""

import time
import board
import digitalio
# https://docs.circuitpython.org/projects/midi/en/latest/api.html
import usb_midi
import adafruit_midi
# pylint: disable=unused-import
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.program_change import ProgramChange

#  midi channel setup
midi_in_channel = 1
midi_out_channel = 1
#  midi setup
#  USB is setup as the input

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    midi_out=None,
    in_channel=(midi_in_channel - 1),
    out_channel=(midi_out_channel - 1),
    debug=False,
)

GATE = digitalio.DigitalInOut(board.D3)
GATE.direction = digitalio.Direction.OUTPUT
CLK = digitalio.DigitalInOut(board.D4)
CLK.direction = digitalio.Direction.OUTPUT
 
notesOn = 0
while True:
#     GATE.value = False    # high to turn off
#     time.sleep(0.5)
#     GATE.value = True   # low to turn on
#     time.sleep(0.5)
#     CLK.value = False    # high to turn off
#     time.sleep(1.5)
#     CLK.value = True    # high to turn off
#     time.sleep(1.5)
    midi_msg = midi.receive()
    if midi_msg is not None:
        if isinstance(midi_msg, NoteOn):
           print("Note On", midi_msg.note, "channel",midi_msg.channel + 1,)
           notesOn += 1
           print("Notes On =",notesOn)
        elif isinstance(midi_msg, NoteOff):
           print("Note Off", midi_msg.note, "channel",midi_msg.channel + 1,)
           notesOn -= 1
        elif isinstance(midi_msg, ControlChange):
            print("Control change")
        elif isinstance(midi_msg, ProgramChange):
            print("Program change")
        else:  # Other messages
            print(midi_msg)
