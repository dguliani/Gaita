#!/usr/bin/python
import pyb
import math
from pyb import I2C
import ESP8266
import BNO055
import SensorBase
import sys
import array
import struct

class IMULogger(object):
    def __init__(self):
        # Initializing
        self.switch = pyb.Switch()
        self.start_led = pyb.LED(2)
        self.sensor_base = SensorBase.SensorBase()

        # Constants
        self.sampling_delay = 6 #ms delay
        self.standard_delay = 500 #ms
        self.test_time = 30000 #ms

        # Flicker to indicate start of test
        for i in range(3):
            self.start_led.on()
            pyb.delay(self.standard_delay)
            self.start_led.off()
            pyb.delay(self.standard_delay)

        while not self.switch():
            pass

        log = open('/sd/06_02_17_raw_walk_random.csv', 'w')
        pyb.delay(self.standard_delay)

        self.start_time = pyb.millis();
        time = 0;

        self.start_led.on()

        while not self.switch() and time < self.test_time:
            # TODO Sample and record gravity
            ax, ay, az, gx, gy, gz, mx, my, mz, yaw, roll, pitch = self.sensor_base.sample_motion()
            fsr1, fsr2, fsr3 = self.sensor_base.sample_fsr()
            time = pyb.elapsed_millis(self.start_time)

            # ax = 0 if (abs(ax) < 1) else ax
            # ay = 0 if (abs(ay) < 1) else ay
            # az = 0 if (abs(az) < 1) else az
            # print("ax: {}  \t ay: {} \t , az: {}".format(ax, ay, az))
            # print("fsr1: {}  \t fsr2: {} \t , fsr3: {}".format(fsr1, fsr2, fsr3))

            log.write('{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(time, ax, ay, az, gx, gy, gz, mx, my, mz, roll, pitch, yaw, fsr1, fsr2, fsr3))
            # log.write('{},{},{}, {}\n'.format(time, ax, ay, az))
            pyb.delay(self.sampling_delay)

        log.close()

        # Flicker to indicate end of test
        # self.start_led.on()
        # pyb.delay(self.standard_delay)
        self.start_led.off()


if __name__ == "__main__":
    test = IMULogger()
    del test

