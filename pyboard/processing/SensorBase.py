#!/usr/bin/python
import pyb
import math
from pyb import I2C
import ESP8266
import BNO055
import sys
import array
import struct

class SensorBase(object):
    # Below is calibration data stored from a calibration test performed on 14/11/16 - good starting point
    IMU_CALDATA = array.array('b', [-10, -1, -12, -1, 2, 0, 40, 0, -21, -1, 80, 0, -2, -1, 0, 0, 0, 0, -24, 3, 121, 3])

    def __init__(self):
        # Initializing IMU
        self.imu_startup_procedure()

    def imu_startup_procedure(self):
        self.bno = BNO055.BNO055(i2c=1)
        if not self.bno.begin():
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

        status, self_test, error = self.bno.get_system_status()
        print('System status: {0}'.format(status))
        print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))

        # Print out an error if system status is in error mode.
        if status == 0x01:
            print('System error: {0}'.format(error))
            print('See datasheet section 4.3.59 for the meaning.')

        self.bno.set_calibration(self.IMU_CALDATA)
        print(self.bno.get_calibration())
        # Print BNO055 software revision and other diagnostic data.
        sw, bl, accel, mag, gyro = self.bno.get_revision()
        print('Software version:   {0}'.format(sw))
        print('Bootloader version: {0}'.format(bl))
        print('Accelerometer ID:   0x{0:02X}'.format(accel))
        print('Magnetometer ID:    0x{0:02X}'.format(mag))
        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

    def sample_motion(self):
        # Sample IMU
        ax, ay, az = self.bno.read_linear_acceleration()
        gx, gy, gz = self.bno.read_gyroscope()
        mx, my, mz = self.bno.read_magnetometer()
        yaw, roll, pitch = self.bno.read_euler()
        return (ax, ay, az, gx, gy, gz, mx, my, mz, yaw, roll, pitch)

    def sample_temp(self):
        temp = self.bno.read_temp()
        return temp

    def sample_gravity(self):
        grx, gry, grz = self.bno.read_gravity()
        return (grx, gry, grz)

if __name__ == "__main__":
    sensor_base = SensorBase()
    del sensor_base

