#!/usr/bin/python

import sys
from pyb import UART
import pyb
import struct
import constants

UART_DEFAULT_PORT = 2
ESP8266_DEFAULT_BAUDRATE =  115200 #Experimentally derived for our ESP8266 chips
DEVEL_SSID = "TellMyWifiLover" #"NETGEAR75"
DEVEL_PWD = "pineapple" #"rockylotus847"#
#UDP_DEFAULT_IP = "127.0.0.39"
UDP_DEFAULT_IP = "192.168.0.101" #this should be the broadcast address of the laptop to stream to
UDP_DEFAULT_PORT = 5005

def enum(**enums):
    return type('Enum', (), enums)

Status = enum(ERR='ERROR', OK=['OK', 'ready', 'no change', 'SEND OK', 'ALREAY CONNECT'], BUSY='busy')
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class ESP8266(object):

    def __init__(self, rst=None, port=UART_DEFAULT_PORT, baud_rate=ESP8266_DEFAULT_BAUDRATE, parity=None,
                ssid=DEVEL_SSID, pwd=DEVEL_PWD):

        print("Starting wifi module")
        self.serial = UART(port, baud_rate)
        self.ssid = ssid
        self.pwd = pwd
        self.IP = None
        self.connected = False

        self.startup_procedure()
        self.udp_connect()
        # self.udb_send_sample_num_stream()

    # TODO ADD Retry
    # Set expected_return parameter to None in order to retrieve full response
    def _serial_send(self, command, expected_return=Status.OK, timeout=1000):
        self.serial.write(command + "\r\n")
        response_received = 0
        start_time = pyb.millis();
        time = 0;
        while(response_received == 0 and time < timeout):
            # Small delay between response checks
            time = pyb.elapsed_millis(start_time)

            pyb.delay(80)
            ret = self.serial.readline()
            if(ret == None):
                ret = self.serial.readline()
            else:
                ret = ret.decode("utf-8")
                print(ret)
                if( expected_return is None):
                    if( '\n' in ret and len(ret) < 4):
                        pass # Got carriage return, wait for other response
                    elif(command in ret):
                        pass # Sometimes you get the command returned; this is not what we are looking for
                    else:
                        return(True, ret)
                else:
                    if( ret.strip() in expected_return):
                        return (True, ret)
                    elif(Status.ERR in ret): # Maybe should through error here
                        return (False, ret)
                    else:
                        pass
        return(False,'Timeout')

    def startup_procedure(self):
        passed, ret = self._serial_send( "AT", expected_return=Status.OK )
        if passed:
            passed, ret = self._serial_send( "AT+CWMODE=1") # set device mode (1=client, 2=AP, 3=both)
            passed, ret = self._serial_send( "AT+CWJAP=\""+self.ssid+"\",\""+self.pwd+"\"" ) # connect
            passed, ret = self._serial_send( "AT+CIFSR", expected_return=None) # check IP address
            if passed:
                self.IP = ret
                print("Connected to {} with IP: {}".format(self.ssid, ret))
                self.connected = True
            else:
                print("Failed to connect: {}".format(ret))
                self.connected = False

    def chunk_and_send(self, data):
        pass

    def _chunk(self):
        pass
    # UDP Functions
    # TODO Something wrong with this reset
    def reset_wifi(self):
        self._serial_send('AT+RST')
        pyb.delay(constants.ESP_ST_DELAY)

    def udp_connect(self):
        # Setup UDP Connection
        if self.connected:
            passed, ret = self._serial_send("AT+CIPMUX=0") # single connection mode
            passed, ret = self._serial_send("AT+CIPSTART=\"UDP\",\"" + UDP_DEFAULT_IP + "\",5005", timeout=10000)
            if not passed:
                print("Could not establish UDP connection: {}".format(ret))
            else:
                return True
        else:
            self.connected = False
            return False

    def udp_send(self, data):
        data_length = len(data)
        cmd = "AT+CIPSEND="+str(data_length)
        print("Trying to send data of length {}".format(str(data_length)))
        passed, ret = self._serial_send(cmd, expected_return=['>'])
        if passed:
            data = data
            passed, ret = self._serial_send(data)
            if passed:
                print("Sent: {}".format(data))
            else:
                print("Send Error: {}".format(ret))
        else:
            print("Unable to send, not recieving > from ESP: {}".format(ret))


    def udp_close(self):
        self._serial_send("AT+CIPCLOSE")

    def udb_send_sample_num_stream(self):
        if self.connected and self.udp_connect():
            data_counter = 990
            while(data_counter < 1000):
                self.udp_send(str(data_counter) + "LALALALALALALALALALALAL\r\n")
                data_counter = data_counter + 1
            self.udp_close()

if __name__ == "__main__":
    ESP8266_obj = ESP8266()
    del ESP8266_obj
