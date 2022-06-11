from machine import I2C
from dht20 import DHT20
i2c = I2C(0)
dht20 = DHT20(i2c)
temper = dht20.dht20_temperature()
humidity = dht20.dht20_humidity()
print("temper :    " + str(temper))
print("humidity : " + str(humidity))