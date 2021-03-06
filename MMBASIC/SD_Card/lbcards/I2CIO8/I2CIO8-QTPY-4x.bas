' Test I2CIO-8 card (I2CIO8-QTPY-4x.bas)
'
' Bounce a LED across the LEDs on 4 cards
'
' Running on QTPy49 card
'   http://land-boards.com/blwiki/index.php?title=QTPy49
' XIAO RP2040 card
'   http://land-boards.com/blwiki/index.php?title=QT_Py_(RP2040_based)
'
' I2CIO-8 card Wiki page
' http://land-boards.com/blwiki/index.php?title=I2CIO-8
'
' MCP23008 I2C2 Expander
' I2C2 Address jumpers set to H20-H23
' Uses I2C0, PINS GP4, GP5
'
' I2CIO-8 to MCP23008 port mapping
'   GPIO0-3 = LEDs = OUT
'   GPIO4-7 = Jumpers = IN
'     Jumpers are low when inserted
'     Program inverts the inputs
'
' Doug Gilliland
' Land Boards, 2022
'

Print "Bounce a 1 across the LEDs (I2CIO8-Bounce-0.bas)"
Print "Hit a key to stop"

MCP23008_IODIR   = &H00
MCP23008_IPOL    = &H01
MCP23008_GPINTEN = &H02
MCP23008_DEFVAL  = &H03
MCP23008_INTCON  = &H04
MCP23008_IOCON   = &H05
MCP23008_GPPU    = &H06
MCP23008_INTF    = &H07
MCP23008_INTCAP  = &H08
MCP23008_GPIO    = &H09
MCP23008_OLAT    = &H0A

waitTime = 200

numCards = 4

SetPin GP6, GP7, I2C2
I2C2 OPEN 400, 100:'400 KHz, 100 mS timeout
For i2cadr = &H20 To &H20 + numCards-1
  initMCP23008(i2cadr)
Next i2cadr

' Do the program loop

' Bounce left across LEDs
forever:
For i2cadr = &H20 To &H20 + numCards-1
ledval = 1
    nextled1:
    WriteLEDs(i2cadr, ledval)
    Pause waitTime
    ledval = ledval * 2
    If Inkey$ <> "" GoTo done
    If ledval < 16 GoTo nextled1
  WriteLEDs(i2cadr, 0)
Next i2cadr
GoTo forever

Sub WriteLEDs(i2cAdr, LEDVAL)
  I2C2 WRITE i2cAdr, 0, 2, &H0A, LEDVAL:'OLAT WRITE OUT
End Sub

Sub initMCP23008(i2cadr)
  I2C2 WRITE i2cadr, 0, 2, MCP23008_IODIR, &HF0:'IODIR
  If MM.I2C = 0 GoTo skipFail
  If MM.I2C = 1 Then Print "I2C2 failed - Received NACK responce"
  GoTo done
skipFail:
  I2C2 WRITE i2cadr, 0, 2, MCP23008_IPOL, &HF0:'IPOL INVERT INPUTS
  I2C2 WRITE i2cadr, 0, 2, MCP23008_GPINTEN, &HF0:'Interrupt enables
  I2C2 WRITE i2cadr, 0, 2, MCP23008_INTCON, &H00:'COMPARE TO PREVIOUS VAL
  I2C2 WRITE i2cadr, 0, 2, MCP23008_IOCON, &H24:'NOT SEQ, ODR/LOW
End Sub

done:
Print "Done bouncing the LEDs"                 