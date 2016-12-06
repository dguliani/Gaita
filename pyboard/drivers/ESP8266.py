#!/usr/bin/python

# import logging
# import sys, serial
# from time import *
# import datetime, string
import sys
from pyb import UART
import pyb



UART_DEFAULT_PORT = 4
ESP8266_DEFAULT_BAUDRATE = 9600
DEVEL_SSID = "TellMyWifiLover"
DEVEL_PWD = "pineapple"

def enum(**enums):
    return type('Enum', (), enums)

Status = enum(ERR='ERROR', OK=['OK', 'ready', 'no change'], BUSY='busy')
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class ESP8266(object):

    def __init__(self, rst=None, port=UART_DEFAULT_PORT, baud_rate=ESP8266_DEFAULT_BAUDRATE, parity=None,
                 stop=ESP8266_DEFAULT_STOP, ssid=DEVEL_SSID, pwd=DEVEL_PWD):

        self.serial = UART(port, baud_rate)


        self._serial_send( "AT" )
        # send_cmd( "AT+RST", 5 ) # NOTE: seems to cause problems that require manually reset (pulling down the RST pin)
        # sleep(3)
        self._serial_send( "AT+CWMODE=1" ) # set device mode (1=client, 2=AP, 3=both)
        #The mode will be changed on Olimex MOD-WIFI-ESP8266-DEV only after a reset
        #The command below will reset the device
        self._serial_send( "AT+RST");
        self._serial_send( "AT+CWLAP", 10) # scan for WiFi hotspots
        self._serial_send( "AT+CWJAP=\""+ssid+"\",\""+pwd+"\"", 5 ) # connect
        self.IP = self._serial_send( "AT+CIFSR", 5) # check IP address

    def _serial_send(self, command, ack=True, waitTm=1, retry=5):

        for i in range(retry):
            self.serial.write(command + "\r\n")
            ret = self.serial.readline()
            while('busy' in ret):
                ret = self.serial.readline()
                if( ret in Status.OK): break
                if( ret in Status.ERR ): break

        return ret
            # pyb.delay()
