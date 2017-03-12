#!/usr/bin/python
import array

# Relating to Pyboard
ADC_MIN = 0
ADC_MAX = 4095

# Relating to IMU
IMU_CALDATA = array.array('b', [-10, -1, -12, -1, 2, 0, 40, 0, -21, -1, 80, 0, -2, -1, 0, 0, 0, 0, -24, 3, 121, 3])
BNO055_I2C_INDEX = 1

# Relating to FSR
FSR_VOLTAGE_MIN = 0 #mV
FSR_VOLTAGE_MAX = 3300 #mV
FSR_VOLTAGE_THRESOLD = 10 #mV
FSR_PAR_RES = 10000 #10K
FSR_CONDUCTANCE = 1000000 #Conductance in MicroOhms

# ESP
ESP_ST_DELAY = 250