# synth_midi_ctl_01_002.py

"""
Based on midi_inoutdemo.py from
\circuitpythonBundles\adafruit-circuitpython-bundle-7.x-mpy-20220611\examples
Runs on board
    http://land-boards.com/blwiki/index.php?title=SYNTH-MIDI-CTL-01
XIAO RP2040 CPU
    http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)#Seeeduino_XIAO_RP2040
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

#  midi setup
#  USB is setup as the input

#  midi channel setup
midi_in_channel = 1
midi_out_channel = 1

# MIDI instance constructor
midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    midi_out=None,
    in_channel=(midi_in_channel - 1),
    out_channel=(midi_out_channel - 1),
    debug=False,
)

GATE = digitalio.DigitalInOut(board.D3)
GATE.direction = digitalio.Direction.OUTPUT
GATE.value = True   # high to turn off

CLK = digitalio.DigitalInOut(board.D4)
CLK.direction = digitalio.Direction.OUTPUT
CLK.value = True    # high to turn off

GATE.value = False    # low to turn on
time.sleep(1)
GATE.value = True   # high to turn off
 
CLK.value = False    # low to turn on
time.sleep(1)
CLK.value = True   # high to turn off

notesOn = 0
while True:
    midi_msg = midi.receive()
    if midi_msg is not None:
        if isinstance(midi_msg, NoteOn):
           # print("Note On", midi_msg.note, "channel",midi_msg.channel + 1,)
           notesOn += 1
           # print("Notes On =",notesOn)
           if notesOn == 1:
               print("First Note",midi_msg.note,"velocity",midi_msg.velocity)
        elif isinstance(midi_msg, NoteOff):
           # print("Note Off", midi_msg.note, "channel",midi_msg.channel + 1,)
           notesOn -= 1
        elif isinstance(midi_msg, ControlChange):
            print("Control change - control =", midi_msg.control, ", value =", midi_msg.value)
        elif isinstance(midi_msg, ProgramChange):
            print("Program change, patch =", midi_msg.patch)
        else:  # Other messages
            print(midi_msg)
