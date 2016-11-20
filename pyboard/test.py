#!/usr/bin/python
import pyb
import math
from pyb import I2C
import BNO055
import sys
import array

class SensorBase(object):
    # Below is calibration data stored from a calibration test performed on 14/11/16 - good starting point
    IMU_CALDATA = array.array('b', [-10, -1, -12, -1, 2, 0, 40, 0, -21, -1, 80, 0, -2, -1, 0, 0, 0, 0, -24, 3, 121, 3])

    def __init__(self):
        self.switch = pyb.Switch()
        self.imu_startup_procedure()

        self.static_delay = 10 #ms delay
        self.zero_count = 0
        self.last_moving = False
        count = 0

        # log = open('/sd/19_11_16_walk_sim.csv', 'w')
        # pyb.delay(500)

        self.last_vel =     {'x':0, 'y':0, 'z':0}
        self.last_pos =     {'x':0, 'y':0, 'z':0}
        self.last_accel =   {'x':0, 'y':0, 'z':0}
        self.vel =          {'x':0, 'y':0, 'z':0}
        self.pos =          {'x':0, 'y':0, 'z':0}
        self.accel =        {'x':0, 'y':0, 'z':0}

        while not self.switch() and count < 1000:
            self.sample()
            # count = count + 1
            # log.write('{},{},{},{}\n'.format(count*self.static_delay,self.last_pos['x'],self.last_pos['y'],self.last_pos['z']))
            pyb.delay(self.static_delay)

        # log.close()

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

        # self.bno.set_calibration(self.IMU_CALDATA)
        print(self.bno.get_calibration())
        # Print BNO055 software revision and other diagnostic data.
        sw, bl, accel, mag, gyro = self.bno.get_revision()
        print('Software version:   {0}'.format(sw))
        print('Bootloader version: {0}'.format(bl))
        print('Accelerometer ID:   0x{0:02X}'.format(accel))
        print('Magnetometer ID:    0x{0:02X}'.format(mag))
        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

    def sample(self):
        # Sample IMU
        # heading, roll, pitch = self.bno.read_euler()
        x, y, z = self.bno.read_linear_acceleration()
        gx, gy, gz = self.bno.read_gyroscope()
        timestep = self.static_delay/1000

        gyr_threshold = 0.08
        moving = True if (abs(gx) > gyr_threshold or abs(gy) > gyr_threshold or abs(gz) > gyr_threshold) else False

        accel_threshold = 0.05
        self.accel['x'] = x if moving else 0
        self.accel['y'] = y if moving else 0
        self.accel['z'] = z if moving else 0

        if not moving and not self.last_moving:
            self.zero_count = self.zero_count + 1

            if self.zero_count % 5 is 0:
                self.last_vel['x'] = 0
                self.last_vel['y'] = 0
                self.last_vel['z'] = 0
                # print("Resetting velocity ")

            if self.zero_count > 12:
                self.last_pos['x'] = 0
                self.last_pos['y'] = 0
                self.last_pos['z'] = 0
                self.zero_count = 0
                # self.static_delay = 500
                # print("Resetting position")

        elif not moving:
            self.zero_count = 0
        # else:
            # self.static_delay = 10

        # self.vel['x'] = self.last_vel['x'] + ((self.last_accel['x'] + (self.accel['x']-self.last_accel['x'])/2) * (self.static_delay/1000))
        # self.vel['y'] = self.last_vel['y'] + ((self.last_accel['y'] + (self.accel['y']-self.last_accel['y'])/2) * (self.static_delay/1000))
        # self.vel['z'] = self.last_vel['z'] + ((self.last_accel['z'] + (self.accel['z']-self.last_accel['z'])/2) * (self.static_delay/1000))

        # self.pos['x'] = self.last_pos['x'] + ((self.last_vel['x'] + (self.vel['x']-self.last_vel['x'])/2) * (self.static_delay/1000))
        # self.pos['y'] = self.last_pos['y'] + ((self.last_vel['y'] + (self.vel['y']-self.last_vel['y'])/2) * (self.static_delay/1000))
        # self.pos['z'] = self.last_pos['z'] + ((self.last_vel['z'] + (self.vel['z']-self.last_vel['z'])/2) * (self.static_delay/1000))

        self.vel['x'] = self.last_vel['x'] + (self.accel['x'] * timestep)
        self.vel['y'] = self.last_vel['y'] + (self.accel['y'] * timestep)
        self.vel['z'] = self.last_vel['z'] + (self.accel['z'] * timestep)

        self.pos['x'] = self.last_pos['x'] + (self.vel['x'] * timestep)
        self.pos['y'] = self.last_pos['y'] + (self.vel['y'] * timestep)
        self.pos['z'] = self.last_pos['z'] + (self.vel['z'] * timestep)

        # Setting last iteration of variables
        self.last_accel['x'] = self.accel['x']
        self.last_accel['y'] = self.accel['y']
        self.last_accel['z'] = self.accel['z']
        self.last_vel['x'] = self.vel['x']
        self.last_vel['y'] = self.vel['y']
        self.last_vel['z'] = self.vel['z']
        self.last_pos['x'] = self.pos['x']
        self.last_pos['y'] = self.pos['y']
        self.last_pos['z'] = self.pos['z']

        self.last_moving = moving

        # print('pos x: {}, pos y: {}, pos z: {}'.format(self.pos['x'], self.pos['y'], self.pos['z']))
        # print('vel x: {}, vel y: {}, vel z: {}'.format(self.vel['x'], self.vel['y'], self.vel['z']))
        # print('accel x: {} accel y: {} accel z: {} \t gyr x: {} gyr y: {} gyr z: {}'.format(self.accel['x'],self.accel['y'],self.accel['z'],gx,gy,gz))
q        # print('accel x: {} accel y: {} accel z: {}, \t moving: {}'.format(self.accel['x'],self.accel['y'],self.accel['z'], moving))
        # print(moving)

        # Sample FSR

if __name__ == "__main__":
    sensor_base = SensorBase()
    del sensor_base

