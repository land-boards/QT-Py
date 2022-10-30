# SYNTH-MIDI-CTL-01_RND_Pitch-Mod.py
#
# Generate random pitch and mod CV values to ER-VCO3-01 card
# Speed pot adjusts notes rate from 2 secs per note to ~15 notes/sec (7 o-clock to 3 o-clock)
# Set speed pot from 3 o-clock to 5 o-clock to stop (set both CVs to 0V)
# Set speed pot past 5 o-clock to exit (used for debugging)
# Added notes dict to make only actual notes
# Random notes in a range of offsets

"""
Hardware is based on
HAGIWO "MIDI to CV module for 900 yen - Modular synth self-made"
    https://note.com/solder_state/n/n17e028497ebaHAGIWO
    https://www.youtube.com/watch?v=bHiZhLAntNI
HAGIWO Arduino code
    https://github.com/land-boards/lb-Arduino-Code/blob/master/LBCards/SYNTHS/SYNTHMIDICTL01/SYNTHMIDICTL01.ino
CircuitPython MIDI code - midi_inoutdemo.py from
    \circuitpythonBundles\adafruit-circuitpython-bundle-7.x-mpy-20220611\examples
Runs on board (Wiki Page)
    http://land-boards.com/blwiki/index.php?title=SYNTH-MIDI-CTL-01
Differences from HAGIWO build
    Code is Python not Arduino
    HAGIWO runs on Arduino NANO, this runs on XIAO RP2040 (5V vs 3.3V)
XIAO RP2040 Pins
    A0, P26 = CLK_POT
    D1 = Unused
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
    3.3V operation
Gate output for note, 50 mSec between notes
CVs generated by MCP4822 Dual 12-bit D/A

Only plays 1 note at a time on mono synth
HAGIWO code uses 2nd CV as modulation input to the VCO which uses  as control
Pitch Blend adjusts Pitch CV
MIDI clock rate is divide by 24, 12, 6, 3 as determine by CLK Rate pot
"""

import time
import board
import digitalio
import busio
import analogio

import microcontroller
import math
import random

def setGate(gateVal):
    if gateVal:
        GATE.value = False
    else:
        GATE.value = True

def writeCVD2AChannel(channel,outval):
    outval &= 0x0fff
    if channel == 0:
        outval += 0x3000
    elif channel == 1:
        outval += 0xB000
    writeBytes = bytes([((outval >> 8) & 0xff), outval & 0xFF])
    while not spi.try_lock():
        pass
    spi.configure(baudrate=5000000, phase=0, polarity=0)
    cs.value = False
    spi.write(writeBytes)
    cs.value = True
    spi.unlock()
    lddac.value = False
    microcontroller.delay_us(2)
    lddac.value = True
    
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

# Turn pot from values of ~0 to ~65536 into log values from ~0 to ~15
def normalizePot():
    clkSpeed = clkSpeedPotVal.value
#    print("Analog pot val -",clkSpeed,end='')
    logSpeed = math.log(clkSpeed,2)
#    print(", log of pot",logSpeed,end='')
    # Normalize pot
    logSpeed -= 8.0
    if logSpeed < 0.0:
       logSpeed = 0.001
#    print(", normalized log of pot",logSpeed,end='')
    microSecDelay = int(1000000.0/logSpeed)
#    print(", Delay",microSecDelay)
    return(microSecDelay)

# Create notes table
# 60 Notes in 5 octaves
def makeNotesCVDict():
    notesDict = {}
    for note in range(0,60):
        notesDict[note] = int(4095.0*note/60.0)
#     print(notesDict)
    return notesDict 

notesDict = makeNotesCVDict()
# print(notesDict)

# Send out random pitch and random modulation
# Rate is variable via pots from ~2 secs per note to ~15 notes/sec
# Note rate is Speed Pot is 7 o-clock to 2 o-clock
# CCW = slowest (~2 secs/note)
# Output muted when Speed Pot is from 3 o-clock to 5 o-clock
# Exit when Speed Pot is 5 o-clock to 7 o-clock
# Turn pot into log pot so control is smoother
state = 'start'
print("Random CV Generator")
modRampValue = 0
noteToPlay = 32
maxNoteOffset = 6
minNoteVal = 16
maxNoteVal = 48
while True:
# while clkSpeedPotVal.value < 60000:
    while clkSpeedPotVal.value < 55000:
        if state != 'clocking':
            print("Clocking state")
            state = 'clocking'
        normalizePot()
#        noteToPlay = random.randint(0,59)
        noteToTryToPlay = noteToPlay + random.randint(-maxNoteOffset,maxNoteOffset)
        stuckCount = 0
        while (noteToTryToPlay < minNoteVal) or (noteToTryToPlay > maxNoteVal):
            noteToTryToPlay = noteToPlay + random.randint(-maxNoteOffset,maxNoteOffset)
            stuckCount += 1
            if stuckCount > 256:
                noteToTryToPlay = 32
                print("Released stuck")
        noteToPlay = noteToTryToPlay
        noteCV = notesDict[noteToPlay]
        writeCVD2AChannel(0,noteCV) # Pitch
        writeCVD2AChannel(1,modRampValue)   # Modulation
        modRampValue += 16
        modRampValue &= 0x0fff
#         if modRampValue & 0x00ff == 0:
#             print("Mod value = ",modRampValue)
        if modRampValue & 0x0fff == 0:
            print("Mod value looping")
        setGate(True)
        loopCount = 0
        for loopCt in range(0,10):
            microcontroller.delay_us((int)(normalizePot()/10))  # Help pot reaction time
        setGate(False)
        microcontroller.delay_us(50000)  # Gate off for 50 mS between notes
    if state != 'muting':
        print('Muted')
        state = 'muting'
        writeCVD2AChannel(0,0) # Zero out CVs when in muted state
        writeCVD2AChannel(1,0)
    time.sleep(0.001)
    # print("Clock Speed Pot =",clkSpeedPotVal.value)
    normalizePot()
writeCVD2AChannel(0,0)    # Zero out CVs when exiting
writeCVD2AChannel(1,0)
print("Exiting out to Python Shell")
