from machine import Pin

button = Pin(18, Pin.IN, Pin.PULL_UP)#按键接p18
button.irq(lambda pin: InterruptsButton(),Pin.IRQ_FALLING)#设置按键中断
led = Pin(16, Pin.OUT)#led灯接p16
tmp = 0
'''按键中断函数，按下按键时改变灯的状态'''
def InterruptsButton(): #按键输入
    global tmp
    tmp = ~tmp
    led.value(tmp)
while True:  
    pass