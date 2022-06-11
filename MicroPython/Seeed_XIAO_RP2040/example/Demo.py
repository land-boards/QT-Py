from machine import Pin, I2C, ADC, UART, SPI, PWM
from time import sleep
from ssd1306 import SSD1306_I2C
from dht11 import *

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=200000)#oled 接i2c1口
oled = SSD1306_I2C(128, 64, i2c)
dht2 = DHT(20) #温湿度传感器接D20口
adc = ADC(2) #ADC输入（旋钮电位器）接A0
pwm = PWM(Pin(27))#DAC输出（蜂鸣器）接A1
button = Pin(18, Pin.IN, Pin.PULL_UP)#按键接p18
button.irq(lambda pin: InterruptsButton(),Pin.IRQ_FALLING)#设置按键中断
led = Pin(16, Pin.OUT)#led灯接p16
uart = UART(0, baudrate=115200)

tmp = 0

'''按键中断函数，按下按键时改变灯的状态'''
def InterruptsButton(): #按键输入
    global tmp
    tmp = ~tmp
    led.value(tmp)
    
#进入循环
while True:  
    '''串口测试'''
    #通过uart发送“hello”
    uart.write("hello\n")
    sleep(0.01)
    if uart.any():
        # 如果有数据 读入一行数据返回数据为字节类型
        # 例如  b'hello\n'
        buff = uart.readline()
        # 将收到的信息打印在终端
        print('Echo Byte: {}'.format(buff))
        
    '''SPI口测试'''
    #spi = SPI(0)
    #spi.init(115200)
    #spi.write('0xFC')
    #buf = spi.read(5)
    #buf = bytearray(16)
    #spi.write_readinto('out', buf)
    #print(buf)
    
    '''模拟口测试'''
    val = adc.read_u16()#读取A2口adc值（65535~0）
    #驱动蜂鸣器，adc值小于300时关闭蜂鸣器
    if val > 300:
        pwm.freq(int(val/30))
        pwm.duty_u16(1000)
    else:
        pwm.duty_u16(0)
    
    
    '''GPIO口测试'''
    #温湿度传感器DHT11测试
    temp,humid = dht2.readTempHumid()#temp:温度 humid:湿度

    
    '''I2C口测试'''    
    ''' oled显示器测试'''
    oled.fill(0)#清屏
    oled.text("Temp:  " + str(temp),0,0)#第一行显示温度
    oled.text("Humid: " + str(humid),0,8)
    oled.text("Val:   " + str(val),0,16)
    oled.text("Buff:  " + str(buff),0,24)
    oled.text("led:   "+ str(tmp and "on" or "off") ,0,32)
    oled.show()
    
    '''文件管理测试'''
    file = open("test.txt", "w")#打开test.txt文件，写入以下信息
    file.write("Temp:  " + str(temp) + "\n")
    file.write("Humid: " + str(humid) + "\n")
    file.write("Val:   " + str(val) + "\n")
    file.write("Buff:  " + str(buff)+ "\n")
    file.close()