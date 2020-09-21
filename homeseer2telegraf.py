#!/usr/bin/env python3

import enum
import re
import socket
import collections
from pyhomeseer.homeseer_client import HomeSeerClient

debug = 1

seenDevices = collections.defaultdict()

# Telegraf Configuration
telegrafHost = '192.168.0.125'
telegrafPort = 8094
telegrafProtocol = 'tcp'

# HomeSeer Configuration
hsHost = '192.168.0.125'
hsTcpPort = 11000
hsHttpPort = 9898
hsTcpProtocol = 'tcp'
hsUser = 'apiaccess'
hsPass = 'faith'

# Variables and Literals
# To install enum34 for python: sudo apt install python-enum34
seenDevices = collections.defaultdict()
action = "action"
deviceID = "deviceID"
oldVal = "oldVal"
newVal = "newVal"

def str2byte(string):
    return bytes(string, "utf-8")

def byte2str(bytestr):
    return bytestr.decode("utf-8")

def keyvalpair(key, val):
    return "=".join((key,val))

def stripws(string):
    return "".join(string.split())

# HomeSeer JSON Reader
hsJson = HomeSeerClient(hsHost, hsHttpPort, hsUser, hsPass)

# Telegraf Socket
#tSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tSocket.connect((telegrafHost, telegrafPort))
#tSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
#tSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
#tSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)

print("Successfully connected to Telegraf")

# HomeSeer Socket
hsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hsSocket.connect((hsHost, hsTcpPort))
hsSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
hsSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
hsSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)

print("Successfully connected to HomeSeer")

# Auth to HomeSeer
auth = ",".join(("au",hsUser,hsPass))
hsSocket.sendall(bytes(auth, 'utf-8'))

print("debug mode: " + str(debug))

while True:
    response = ""
    temp = ""

    print("Waiting for next message")
    response = byte2str(hsSocket.recv(1024))
    temp = response.strip().split(",")

    event = ""
    if (len(temp) == 4):
        print("Received new event")
        event = { action: temp[0], deviceID: temp[1], oldVal: temp[2], newVal: temp[3] }

    # if the event is not a DC, then skip to the next iteration
    if not event[action] == "DC":
        continue

    if not event[deviceID] in seenDevices:
        if debug: 
            print(",".join(("[1]", event[action], event[deviceID], event[oldVal], event[newVal])))

        print("Reqeusting device info")
        device = hsJson.get_devices(ref=event[deviceID])
        seenDevices[event[deviceID]] = device
        print(device)

    if event[deviceID] in seenDevices:

        tSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tSocket.connect((telegrafHost, telegrafPort))
        tSocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        tSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        tSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)

        device = seenDevices[event[deviceID]][0]
        print("Publishing to Telegraf")
        deviceName = "\\".join((device.location2, device.location))
        tPayload = "hs_device," + keyvalpair("device",stripws(deviceName)) + " " + keyvalpair(stripws(device.name),event[newVal] + "\n")
        tSocket.send(str2byte(tPayload))
        print("Sent payload to Telegraf: " + tPayload)

        tSocket.close()





