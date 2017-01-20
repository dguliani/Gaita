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
        self.switch = pyb.Switch()
        self.imu_startup_procedure() #TODO thread

        self.start_led = pyb.LED(2)

        self.start_led.on()
        pyb.delay(500)
        self.start_led.off()

        self.static_delay = 10 #ms delay
        self.zero_count = 0
        self.last_moving = False
        count = 0

        log = open('/sd/adrift_nocal_3.csv', 'w')
        pyb.delay(1000)

        self.accel =        {'x':0, 'y':0, 'z':0}
        self.start_time =    pyb.millis();

        # self.esp.udp_connect()
        time = 0;
        while not self.switch() and time < 20000:
            self.sample()
            time = pyb.elapsed_millis(self.start_time)
            log.write('{},{},{},{}\n'.format(time,self.accel['x'],self.accel['y'],self.accel['z']))
            pyb.delay(self.static_delay)

        log.close()

        self.start_led.on()
        pyb.delay(1000)
        self.start_led.off()

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

        self.accel['x'] = x
        self.accel['y'] = y
        self.accel['z'] = z

    ## WIFI ##
    def esp_init(self):
        self.esp = ESP8266.ESP8266()
        print("tried initializing WIFI")

if __name__ == "__main__":
    sensor_base = SensorBase()
    del sensor_base

