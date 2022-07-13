' PROTO16_LEDs.bas - Light all of the output pins one at a time
' Alternate patterns then bounce a LED
'
' MMBASIC code
'
' Running on QTPy49 card
'   http://land-boards.com/blwiki/index.php?title=QTPy49
' XIAO RP2040 card
'   http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)
'
' External MCP23017 cards such as
'   PROTO16-I2C
'     http://land-boards.com/blwiki/index.php?title=PROTO16-I2C
'
' MCP23017 Datasheet
'   https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf
'
' Doug Gillland
' Land Boards LLC 2022
'

MCP23017_I2CADR   = &H20

' MCP23017 internal registers
MCP23017_IODIRA   = &H00
MCP23017_IODIRB   = &H01
MCP23017_IPOLA    = &H02
MCP23017_IPOLB    = &H03
MCP23017_GPINTENA = &H04
MCP23017_GPINTENB = &H05
MCP23017_DEFVALA  = &H06
MCP23017_DEFVALB  = &H07
MCP23017_INTCONA  = &H08
MCP23017_INTCONB  = &H09
MCP23017_IOCON    = &H0A
MCP23017_GPPUA    = &H0C
MCP23017_GPPUB    = &H0D
MCP23017_INTFA    = &H0E
MCP23017_INTFB    = &H0F
MCP23017_INTCAPA  = &H10
MCP23017_INTCAPB  = &H11
MCP23017_GPIOA    = &H12
MCP23017_GPIOB    = &H13
MCP23017_OLATA    = &H14
MCP23017_OLATB    = &H15

Print "Looping through LEDs"
Print "Hit a key to stop"

' Pin setups

' Setup the Interrupt pin
'SetPin GP2,DIN,PULLUP

' Setup the I2C port for the MCP23017
' Applies to all rev cards
SetPin GP6, GP7, I2C2
I2C2 OPEN 400, 100

initMCP23017()

' Alternating patterns
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATA, &H55
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATB, &HAA
Pause 1000
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATA, &HAA
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATB, &H55
Pause 1000
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATA, &H00
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATB, &H00
Pause 100

loopBack:
loopVal = &H01
loop1:
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATA, loopVal
Pause 200
If Inkey$ <> "" GoTo Done
loopVal = loopVal * 2
If loopVal < 256 GoTo loop1
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATA, 0

loopVal = &H80
loop2:
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATB, loopVal
Pause 200
If Inkey$ <> "" GoTo Done
loopVal = loopVal / 2
If loopVal >= 1 GoTo loop2
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATB, 0
GoTo loopBack

Done:
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATA, &H00
I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_OLATB, &H00
Print "Done"
End

Sub initMCP23017()
  'Set all pins to outputs
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_IODIRA, &H00
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_IODIRB, &H00

  'Don't invert inputs
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_IPOLA, &H00
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_IPOLB, &H00

  'Don't interrupt on any pins
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_GPINTENA, &H00
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_GPINTENB, &H00

  'Interrupt compare against previous pin
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_INTCONA, &H00
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_INTCONB, &H00

  'GPIO Pull-ups disabled
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_GPPUA, &H00
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_GPPUB, &H00

  'Bit 7 - BANK = 0 - Bank addresses are sequential
  'Bit 6 - MIRROR = 1 - Connect INTA and INTB internally
  'Bit 5 - SEQOP = 1 - Disable sequential
  'Bit 4 - DISSLW = 0 - SDA slew rate enabled
  'Bit 3 - HAEN - X - MCP23S017 only
  'Bit 2 - ODR = 1 - Interrup is Open Drain so INT can be "shared"
  'Bit 1 - INTPOL = 0 - Active Low Interrupt level
  'Bit 0 = X - Unused
  I2C2 WRITE MCP23017_I2CADR, 0, 2, MCP23017_IOCON, &H64
End Sub
