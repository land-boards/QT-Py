from machine import Pin,PWM
from buzzer import Music
from time import sleep

pwm = PWM(Pin(27))
mu = Music(pwm)

mu.music(8)
sleep(1)
mu.music(7)
sleep(1)
mu.music(6)
sleep(1)
mu.music(5)
sleep(1)
mu.music(4)
sleep(1)
mu.music(3)
sleep(1)
mu.music(2)
sleep(1)
mu.music(1)
sleep(1)
mu.music(0)



