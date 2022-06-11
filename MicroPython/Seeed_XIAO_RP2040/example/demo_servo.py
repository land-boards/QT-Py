from machine import Pin
from servo import SERVO
from time import sleep
servo = SERVO(Pin(27))
a = 180
while True:
    a = a == 0 and 180 or a - 1
    servo.turn(a)
    sleep(0.1)