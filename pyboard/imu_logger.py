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
import pyb

class IMULogger(object):
    def __init__(self):
        # Initializing
        self.switch = pyb.Switch()
        self.start_led = pyb.LED(2)
        self.sensor_base = SensorBase.SensorBase()

        # Constants
        self.sampling_delay = 100 #ms delay
        self.standard_delay = 500 #ms
        self.test_time = 15000 #ms

        # log = open('/sd/23_01_17_raw_log_3_dir_swing.csv', 'w')
        pyb.delay(self.standard_delay)

        self.start_time = pyb.millis();
        time = 0;

        # Flicker to indicate start of test
        self.start_led.on()
        pyb.delay(self.standard_delay)
        self.start_led.off()



        while not self.switch() and time < self.test_time:
            # TODO Sample and record gravity

            # ax, ay, az, gx, gy, gz, mx, my, mz, yaw, roll, pitch = self.sensor_base.sample_motion()
            time = pyb.elapsed_millis(self.start_time)
            fsr = self.sensor_base.sample_fsr()
            if fsr is not None:
                print( fsr )
            # ax = 0 if (abs(ax) < 1) else ax
            # ay = 0 if (abs(ay) < 1) else ay
            # az = 0 if (abs(az) < 1) else az

            # print("roll: {}  \t pitch: {} \t , yaw: {}".format(roll, pitch, yaw))
            # print("ax: {}  \t ay: {} \t , az: {}".format(ax, ay, az))
            # log.write('{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(time, ax, ay, az, gx, gy, gz, mx, my, mz, roll, pitch, yaw))
            pyb.delay(self.sampling_delay)

        # log.close()

        # Flicker to indicate end of test
        self.start_led.on()
        pyb.delay(self.standard_delay)
        self.start_led.off()


if __name__ == "__main__":
    test = IMULogger()
    del test

