# synth_midi_ctl_01_003.py

"""
HAGIWO MIDI to CV module for 900 yen - Modular synth self-made
    https://note.com/solder_state/n/n17e028497ebaHAGIWO
    https://www.youtube.com/watch?v=bHiZhLAntNI
HAGIWO Arduino code
    https://github.com/land-boards/lb-Arduino-Code/blob/master/LBCards/SYNTHS/SYNTHMIDICTL01/SYNTHMIDICTL01.ino
CircuitPython MIDI code - midi_inoutdemo.py from
\circuitpythonBundles\adafruit-circuitpython-bundle-7.x-mpy-20220611\examples
Runs on board
    http://land-boards.com/blwiki/index.php?title=SYNTH-MIDI-CTL-01
Pins
    A0, P26 = CLK_POT
    D2 = SPI_SS
    D3 = Gate (Out)
    D4 = MIDI Clk (Out)
    D5 = SPI_LDAC
    D6/TX - MIDI_Out
    D7/RX = MIDI In
    D8 = SPI_SCK
    D9 = Unused
    D10 = MOSI
XIAO RP2040 CPU
    http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)#Seeeduino_XIAO_RP2040
Adafruit MIDI handler
    https://docs.circuitpython.org/projects/midi/en/latest/index.html
Starts out with USB MIDI
Use MIDI Editor to send out music over USB
    https://midieditor.org/
Gate output goes on for Note On, off for Note Out
CV
MCP4822

Only plays 1 note at a time due to 1 pitch CV output and mono synth
HAGIWO code uses 2nd CV as modulation input to the VCO which uses  as control
Pitch Blend adjusts Pitch CV
MIDI clock rate is divide by 24, 12, 6, 3 as determine by CLK Rate pot
"""

import time
import board
import digitalio
import busio
import analogio
# https://docs.circuitpython.org/projects/midi/en/latest/api.html
import usb_midi
import adafruit_midi
import microcontroller
# pylint: disable=unused-import
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.program_change import ProgramChange

def setGate(gateVal):
    if gateVal:
        GATE.value = False
    else:
        GATE.value = True

def handleFirstNoteOn(note,velocity):
    print("First Note On =",note,", velocity",velocity,end='')
    setGate(True)
    if note < 21:  # Lowest note = 21
        notePitchCV = 0
    elif note > 82: # Highest note is 82 (can't test since MIDIEditor only goes up to note 71)
        notePitchCV = 82
    else:
        notePitchCV = noteToCVTable[note-21]
    print(", Note CV =",notePitchCV)
    writeCVD2A(0x3000 + notePitchCV)
    pass

def handleFirstNoteOff(note):
    print("First Note Off =",note)
    setGate(False)
    writeCVD2A(0x3000)
    pass

def getMIDIClkRate():
    # Observed A/D value: Min = 352, Mac = 65216
    # Arduino has 10-bit range
    # Not sure why CircuitPython has 16-bit values?
    # Pot 7 o-clock to 9 o-clock = 24 (slowest)
    # Pot 9 o-clock to 12 o-clock = 12
    # Pot 12 o-clock to 3 o-clock = 6
    # Pot 3 o-clock to 5 o-clock = 3 (fastest)
    clkSpeed = clkSpeedPotVal.value
#     print("clkSpeed pot val =",clkSpeed)
    if clkSpeed < 9500:
        clkMax = 24
    elif clkSpeed < 29200:
        clkMax = 12
    elif clkSpeed < 53000:
        clkMax = 6
    else:
        clkMax = 3
    return(clkMax)

def setMidiClk(clkValue):
    if clkValue:
        CLK.value = False    # low to turn on
    else:
        CLK.value = True   # high to turn off

def handleMidiClk():
    print("Clock Message")
    MIDIClkDivisor = getMIDIClkRate()
    if clockCount >= MIDIClkDivisor:
       clockCount = 0
    if clockCount == 1:
        setMidiClk(True)
    else:
        setMidiClk(False)
    
def handleControlChange(control, value):
    # https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
    if control == 121:
        print("ControlChange: Reset All Controllers")
        noteOnFlag = False
        writeCVD2A(0)
    elif control == 64:
        if value <= 63:
            print("ControlChange: Damper Pedal off")
        else:
            print("ControlChange: Damper Pedal on")
    elif control == 91:
        print("ControlChange: Effects 1 Depth =",value)
    elif control == 10:
        print("ControlChange: Pan =",value)
    elif control == 7:
        print("ControlChange: Volume =",value)
    elif control == 120:
        print("ControlChange: All Sound Off")
        noteOnFlag = False
        writeCVD2A(0)
    elif control == 123:
        print("ControlChange: All Notes Off")
        noteOnFlag = False
        writeCVD2A(0)
    else:
        print("Other Control change - control =", control, ", value =", value)

valCV0 = 0
valCV1 = 0

def writeCVD2A(outval):
    # print("outval",outval)
    # Lock the bus
    #print("Check lock")
    while not spi.try_lock():
        pass
    spi.configure(baudrate=5000000, phase=0, polarity=0)
    cs.value = False
    spi.write(bytes([((outval >> 8) & 0xff), outval & 0xFF]))
    cs.value = True
    # Need to unlock bus when done
    spi.unlock()
    lddac.value = False
    microcontroller.delay_us(2)
    lddac.value = True
    
def writeCVVals():
# Test routine sends out ramp vals
#     ch0 = 0x3000
#     ch1 = 0xD000
    for val0 in range(4096):
        outval = val0
        writeCVD2A(outval + 0x3000)
        microcontroller.delay_us(1000)

# Set-up MIDI Clock Speed Pot
clkSpeedPotVal = analogio.AnalogIn(board.A0)

# Set up SPI Chip Select pin
cs = digitalio.DigitalInOut(board.D2)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

# Create an interface to the SPI hardware bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI)

lddac = digitalio.DigitalInOut(board.D5)
lddac.direction = digitalio.Direction.OUTPUT
lddac.value = True

# while True:
#     print("CV ramp")
#     writeCVVals()

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

noteToCVTable = [0,      68,  137,  205,  273,  341,  410,  478,  546,  614,  683,  751, \
                 819,   887,  956, 1024, 1092, 1161, 1229, 1297, 1365, 1434, 1502, 1570, \
                 1638, 1707, 1775, 1843, 1911, 1980, 2048, 2116, 2185, 2253, 2321, 2389, \
                 2458, 2526, 2594, 2662, 2731, 2799, 2867, 2935, 3004, 3072, 3140, 3209, \
                 3277, 3345, 3413, 3482, 3550, 3618, 3686, 3755, 3823, 3891, 3959, 4028, \
                 4095]

# print("noteToCVTable =",noteToCVTable)

clockCount = 0

# while True:
#     writeCVVals()

noteOnFlag = False
currentNote = 0
while True:
    midi_msg = midi.receive()
    if midi_msg is not None:
        if isinstance(midi_msg, NoteOn):
#            print("Note On", midi_msg.note, "channel",midi_msg.channel + 1,)
#            print("Notes on count =",notesOn)
           if not noteOnFlag:
               firstNote = midi_msg.note
               handleFirstNoteOn(firstNote, midi_msg.velocity)
               noteOnFlag = True
        elif isinstance(midi_msg, NoteOff):
#            print("Note Off", midi_msg.note, "channel",midi_msg.channel + 1,)
           if noteOnFlag and (midi_msg.note == firstNote):
               handleFirstNoteOff(firstNote)
               noteOnFlag = False
        elif isinstance(midi_msg, ControlChange):
            handleControlChange(midi_msg.control, midi_msg.value)
        elif isinstance(midi_msg, ProgramChange):
            print("Program change, patch =", midi_msg.patch)
        elif isinstance(midi_msg, PitchBend):
            print("PitchBlend")
        elif isinstance(midi_msg, TimingClock):
            print("Timing Clock")
            handleMidiClk()
        else:  # Other messages
            print(midi_msg)
