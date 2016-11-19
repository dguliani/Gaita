#!/usr/bin/python
import pyb
import math
from pyb import I2C
import BNO055
import sys
import array

class SensorBase(object):
    def __init__(self):
        self.switch = pyb.Switch()
        self.leds = [pyb.LED(i+1) for i in range(4)]
        self.tim = pyb.Timer(4)

        self.imu_startup_procedure()

        self.vel = {'x':0, 'y':0, 'z':0}
        self.pos = {'x':0, 'y':0, 'z':0}
        self.static_delay = 200 #ms delay

        self.accel = {'x':0, 'y':0, 'z':0}

        while not self.switch():
            self.sample()
            # integration
            pyb.delay(self.static_delay)

    def imu_startup_procedure(self):
        self.bno = BNO055.BNO055(i2c=1)
        # self.bno = BNO055.BNO055(i2c=1, rst=18)
        if not self.bno.begin():
            # print("Failed to init BNO055! Is the sensor connected?") # throw an error here in the future
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

        status, self_test, error = self.bno.get_system_status()
        print('System status: {0}'.format(status))
        print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))

        # Print out an error if system status is in error mode.
        if status == 0x01:
            print('System error: {0}'.format(error))
            print('See datasheet section 4.3.59 for the meaning.')

        cal_data = array.array('b',self.bno.get_calibration())
        print('Calibration data: {}'.format(cal_data))
        # self.bno.set_calibration(cal_data)

        # Print BNO055 software revision and other diagnostic data.
        sw, bl, accel, mag, gyro = self.bno.get_revision()
        print('Software version:   {0}'.format(sw))
        print('Bootloader version: {0}'.format(bl))
        print('Accelerometer ID:   0x{0:02X}'.format(accel))
        print('Magnetometer ID:    0x{0:02X}'.format(mag))
        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

    def sample(self):
        # Sample IMU
        heading, roll, pitch = self.bno.read_euler()
        # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
        sys, gyro, accel, mag = self.bno.get_calibration_status()
        # Print everything out.
        print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
              heading, roll, pitch, sys, gyro, accel, mag))

        # print(self.bno.get_calibration_status())


        # Sample FSR

if __name__ == "__main__":
    sensor_base = SensorBase()
    del sensor_base

