#

import board
import busio
import time
import usb_cdc

# COM port configuration
baudUnconfig = const(0x00)
baud300 = const(0x01)
baud1200 = const(0x02)
baud9600 = const(0x03)
baud38400 = const(0x04)
baud57600 = const(0x05)
baud115200 = const(0x06)
baudRate = baud9600

straightSerial = const(0x01)
xmodemProtocol = const(0x02)
srecordProtocol = const(0x03)
serProtocol = straightSerial

NoHandshake = const(0x00)
HWHandshake = const(0x01)
XONXOFFHandshake = const(0x02)
EchoHandshake = const(0x03)
handShake = NoHandshake

# dumpFileToSerial() Dump file to UART
def sendChar(txChar):
    uart.write(bytes(txChar, 'utf-8'))

def setUARTConfig():
    global uart
    global uartInit
    uart = busio.UART(board.TX, board.RX, baudrate=115200)
    uartInit = True
    return

# receiveSerial()
def receiveSerial():
    return
    
serialDebug = False
uartInit = False

print("Hello FPGA-ITX-01")
if not uartInit:
    setUARTConfig()
print("UART configured at 115,200 baud")
# usb_cdc.disable()
# usb_cdc.enable(console=True, data=True)
# USBserial = usb_cdc.data

while True:
    readData = uart.read(1)
    if readData != None:
        print(readData)
#     if USBserial.in_waiting > 0:
#         byteV = serial.read(1)
# #        theStr = string(byteV)
#         uart.write(byteV)

