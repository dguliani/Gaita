#!/usr/bin/python
import pyb
import math

switch = pyb.Switch()
leds = [pyb.LED(i+1) for i in range(4)]
accel = pyb.Accel()
tim = pyb.Timer(4)
# tim.init(freq=10)
i = 0
while not switch():
    x = accel.x()
    y = accel.y()
    z = accel.z()

    print('Accel:: x: {}, y: {}, z: {}'.format(x,y,z))
    # a = math.sqrt(accel.x()^2 + accel.y()^2 + accel.z()^2)
    # i = (i + (1 if y > 0 else -1)) % len(leds)
    # leds[i].toggle()
    # print(a)
    # print(tim.counter())

    pyb.delay(10 * max(1, 20 - abs(y)))


