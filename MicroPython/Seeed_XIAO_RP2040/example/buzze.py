from machine import Pin, I2C, ADC, PWM
from time import sleep

adc = ADC(2) #ADC输入（旋钮电位器）接A0
pwm = PWM(Pin(27))#DAC输出（蜂鸣器）接A1

while True: 
    '''模拟口测试'''
    val = adc.read_u16()#读取A2口adc值（65535~0）
    #驱动蜂鸣器，adc值小于300时关闭蜂鸣器
    if val > 300:
        pwm.freq(int(val/30))
        pwm.duty_u16(1000)
    else:
        pwm.duty_u16(0)
    
