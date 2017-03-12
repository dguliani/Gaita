#!/usr/bin/python
# TO DO
# Make sure you're on the TellMyWiFiLover network
import socket

#this should be the IP address of the laptop being used
#MAKE SURE YOU'RE ON THE SAME NETWORK
UDP_IP = "192.168.0.100" #"192.168.1.255"
#UDP_IP = "192.168.1.255"
#UDP_IP="127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    #data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data, addr = sock.recvfrom(16) # buffer size is 32
    print "received message:", data

# import socket

# UDP_IP = "127.0.0.1"
# UDP_PORT = 5005

# sock = socket.socket(socket.AF_INET, # Internet
#                      socket.SOCK_DGRAM) # UDP
# sock.bind((UDP_IP, UDP_PORT))

# while True:
#     data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
#     print "received message:", data