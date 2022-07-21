' OnBoardLEDs.bas - Blink LED

SetPin GP17, DOUT:' Red LED
SetPin GP16, DOUT:' Green LED
SetPin GP25, DOUT:' Blue LED

Pin(GP17)=1:' Turn off Red LED
Pin(GP25)=1:' Turn off Blue LED
Pin(GP16)=1:' Turn off Green LED

loopBack:
Pause 1000
Pin(GP16)=0:' Turn on Green LED
If Inkey$<>"" GoTo endProg
Pause 1000
Pin(GP16)=1:' Turn off Green LED
If Inkey$="" GoTo loopBack

endProg:
End
