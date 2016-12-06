#!/usr/bin/python

# import logging
# import sys, serial
# from time import *
# import datetime, string
import sys
from pyb import UART
import pyb
import struct


UART_DEFAULT_PORT = 4
ESP8266_DEFAULT_BAUDRATE = 9600
DEVEL_SSID = "TellMyWifiLover"
DEVEL_PWD = "pineapple"
UDP_DEFAULT_IP = "127.0.0.39"
UDP_DEFAULT_PORT = 5005

def enum(**enums):
    return type('Enum', (), enums)

Status = enum(ERR='ERROR', OK=['OK', 'ready', 'no change'], BUSY='busy')
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class ESP8266(object):

    def __init__(self, rst=None, port=UART_DEFAULT_PORT, baud_rate=ESP8266_DEFAULT_BAUDRATE, parity=None,
                ssid=DEVEL_SSID, pwd=DEVEL_PWD):

        print("Starting wifi module")
        self.serial = UART(port, baud_rate)

        # self.IP = None
        self._serial_send( "AT" )
        # send_cmd( "AT+RST", 5 ) # NOTE: seems to cause problems that require manually reset (pulling down the RST pin)
        # sleep(3)
        self._serial_send( "AT+CWMODE=1" ) # set device mode (1=client, 2=AP, 3=both)
        #The mode will be changed on Olimex MOD-WIFI-ESP8266-DEV only after a reset
        #The command below will reset the device
        self._serial_send( "AT+RST");
        self._serial_send( "AT+CWLAP", 10) # scan for WiFi hotspots
        # print("Trying to connect to {} with pwd {}".format(ssid, pwd))
        self._serial_send( "AT+CWJAP=\""+ssid+"\",\""+pwd+"\"", 5 ) # connect
        self.IP = self._serial_send( "AT+CIFSR", 5) # check IP address

    def _serial_send(self, command, ack=True, waitTm=1, retry=1): #todo
        print("Sending command {}".format(command))
        for i in range(retry):
            self.serial.write(command + "\r\n")
            ret = self.serial.readline()
            # print("The ret is: {}".format(struct.unpack('i', ret)))
            # print("The ret is: {}".format(struct.unpack('b', ret)))
            # print("The ret is: {}".format(struct.unpack('c', ret)))
            # print("The ret is: {}".format(struct.unpack('s', ret)))
            # print("The ret is: {}".format(struct.unpack('p', ret)))
            print("Got return value {}".format(struct.unpack('c', ret)))
            while('busy' in ret):
                ret = self.serial.readline()
                if( ret in Status.OK): break
                if( ret in Status.ERR ): break

        return ret
            # pyb.delay()

    def udp_connect(self):
        # Setup UDP Connection
        self._serial_send("AT+CIPMUX=0") # single connection mode
        self._serial_send("AT+CIPSTART=1,\"UDP\",\"" + UDP_DEFAULT_IP + "\",5005")

    def udp_send(self, data):
        cmd = "AT+CIPSEND="+str(1)
        self._serial_send(cmd)
        data = ">" + data
        self._serial_send(data)

    def udp_close(self):
        self._serial_send("AT+CIPCLOSE=1")
