# MIDI_Serial_to_USB.py
# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT
# https://docs.circuitpython.org/projects/midi/en/latest/api.html#adafruit_midi

import board
import busio
import usb_midi
import adafruit_midi
# pylint: disable=unused-import
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.program_change import ProgramChange

#  uart setup
uart = busio.UART(board.TX, board.RX, baudrate=31250)
#  midi channel setup
midi_in_channel = 1
midi_out_channel = 1
#  midi setup
#  UART is setup as the input
#  USB is setup as the output
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=usb_midi.ports[1],
    in_channel=(midi_in_channel - 1),
    out_channel=(midi_out_channel - 1),
    debug=True    
)

print("Running")

while True:
    #  receive MIDI message over USB
    msg = midi.receive()
    #  if a message is received...
    if msg is not None:
        #  send that message over UART
#        midi.send(msg)
#        print message to REPL for debugging
        if isinstance(msg, ControlChange):
            print("CC CTL=",end='')
            print(msg.control,end='')
            print(", val=",end='')
            print(msg.value)
        elif isinstance(msg, PitchBend):
            print("Pitch Blend=",msg.pitch_bend)
        else:
            print(msg)
