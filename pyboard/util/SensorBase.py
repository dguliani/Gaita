#!/usr/bin/python
import pyb
import math
from pyb import I2C
import ESP8266
import BNO055
import constants
import sys
import array
import struct

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class SensorBase(object):
    # Below is calibration data stored from a calibration test performed on 14/11/16 - good starting point
    IMU_CALDATA = array.array('b', [-10, -1, -12, -1, 2, 0, 40, 0, -21, -1, 80, 0, -2, -1, 0, 0, 0, 0, -24, 3, 121, 3])
    FSR_ADC_PIN = pyb.Pin.board.Y12

    def __init__(self):
        # Initializing IMU
        self.imu_startup_procedure()

    def imu_startup_procedure(self):
        self.bno = BNO055.BNO055(i2c=constants.BNO055_I2C_INDEX)
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

    def sample_fsr(self):
        adc = pyb.ADC(self.FSR_ADC_PIN)    # create an ADC on pin Y12
        fsr_voltage = translate(adc.read(), constants.ADC_MIN, constants.ADC_MAX, \
                               constants.FSR_VOLTAGE_MIN, constants.FSR_VOLTAGE_MAX)


        if( fsr_voltage > constants.FSR_VOLTAGE_THRESOLD): #10mV threshold
            fsr_resistance = (constants.FSR_VOLTAGE_MAX - fsr_voltage) * constants.FSR_PAR_RES
            fsr_resistance = fsr_resistance/fsr_voltage

            fsr_conductance = constants.FSR_CONDUCTANCE;
            fsr_conductance = fsr_conductance/fsr_resistance;

             # Use the two FSR guide graphs to approximate the force
            if (fsr_conductance <= 1000):
                fsr_force = fsr_conductance/80
            else:
                fsr_force = fsr_conductance - 1000
                fsr_force = fsr_force/30

            return fsr_force

        else:
            return None

if __name__ == "__main__":
    sensor_base = SensorBase()
    del sensor_base

