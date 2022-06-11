from machine import PWM

Freq = (30000,1046,1174,1318,1396,1567,1780,1975,2085)
class Music:
    def __init__(self,pwm1):
        self.pwm = pwm1
                
    def music(self, number):
        self.pwm.freq(Freq[number])
        self.pwm.duty_u16(5000)