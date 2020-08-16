#!/usr/bin/python3

import threading
import paho.mqtt.client as mqtt 
import time
from threading import Lock
import builtins
import json
import subprocess
import shutil
import os

from utilities import Wifi
from utilities import Logger 

BROKER_IP_ADDRESS = "192.168.0.114"
BROKER_USER_NAME = "emmathew"
BROKER_PASSWORD = "!@#JoTo123"


statusInfo = {'connectedToServer':False}
statusInfoMutex = Lock()
mqttClient = mqtt.Client("P1")



println = builtins.print
def print(*args, **kwargs):
	builtins.print(*args, **kwargs, end='')

def updateStatusInfo(status, value):
	blocking = True
	if (statusInfoMutex.acquire(blocking)): 
		if status in statusInfo:
			statusInfo[status] = value
		statusInfoMutex.release()

def readStatusInfo(status):
	blocking = True
	value = None
	if (statusInfoMutex.acquire(blocking)):
		if status in statusInfo:
			value = statusInfo[status]
		statusInfoMutex.release()
	return value

"""The value of rc determines success or not:
        0: Connection successful
        1: Connection refused - incorrect protocol version
        2: Connection refused - invalid client identifier
        3: Connection refused - server unavailable
        4: Connection refused - bad username or password
        5: Connection refused - not authorised
        6-255: Currently unused."""
def callBackOnConnect(client, userdata, flags, rc):
	if rc == 0:
		println("Connected To Server\n")
		updateStatusInfo('connectedToServer', True)
		mqttClient.subscribe("topic/mha/system/in", 0)
	else:
		updateStatusInfo('connectedToServer', False)

def callBackOnDisconnect(client, userdata, rc):
	updateStatusInfo('connectedToServer', False)
	time.sleep(5)
	connectToServer()

def publishMessage(msg):
	mqttClient.publish("topic/mha/system/out", msg)
	print('Message published')


def getApInfo(apList):
	dataList = []
	data = {'macaddr':None,'ssid':'None'}
	for ap in apList:
		shcmd = 'sudo iwlist wlan0 scan essid "' + ap +'"'
		response = subprocess.run(shcmd.split(' '), capture_output=True, timeout=30)
		if response.returncode == 0:
			output = response.stdout.decode("utf-8")
			subString = "Address: "
			if subString in output:
				startIndex = output.find(subString) + len(subString)
				endIndex = startIndex + 17 #17 characters for mac address
				macAddr = output[startIndex:endIndex]
				# Todo: When data base is ready no need to list existing mac address in data
				# base if we have logic for it to autoconnect.
				if macAddr.count(':') == 5: #make sure the mac address is vaid format
					data['macaddr'] = macAddr
					data['ssid'] = ap
					dataList.append(data)
	return dataList



def handleRequest(command, args):
	respMsg = {'type':'response', 'command':command, 'data':None}

	if command == 'scanWifi':
		println("Command recevied to scan wifi")
		apInfo = Wifi.findMhaDevices()
		if len(apInfo) < 1:
			Logger.log(Logger.LogLevel.error, "Unable to find any MHA Devices in accespoint mode")
		else:
			data = []
			for ap in apInfo:
				data.append({'macaddr': Wifi.getMacAddr(ap), 'ssid':Wifi.getSsid(ap)})
			respMsg['data'] = data
			Logger.log(Logger.LogLevel.info, "New APs:" + str(data))
		publishMessage(json.dumps(respMsg))

	if command == 'connectToWifi':
		println('Command Received to connec to Wifi')
		if 'ssid' in args:
			ssid = args['ssid']
			macaddr = ''
			if 'macaddr' in args:
				macaddr = args['macaddr']
			status = {'connectedToWifi': 'True'}
			if connectToWifi(ssid, macaddr) != 0:
				status['connectedToWifi'] = 'False'
			respMsg['data'] = status
			publishMessage(json.dumps(respMsg))



def callBackOnMessage(client, userdata, message):
	println("Message recevied")
	data = json.loads(message.payload)
	if 'type' in data:
		if data['type'] == 'request':
			if 'command' in data:
				args = {}
				if 'args' in data:
					args = data['args']
				threadingObj = threading.Thread(target = handleRequest, args = (data['command'],args,))
				threadingObj.start()
			else:
				println("Invalid Json recevied. 'command' not found")
	else:
		println("Invalid Json received. 'type' not found")



	

def connectToServer():
	if (mqttClient != None):
		mqttClient.username_pw_set(BROKER_USER_NAME,BROKER_PASSWORD)
		
		mqttClient.on_connect = callBackOnConnect
		mqttClient.on_disconnect = callBackOnDisconnect
		mqttClient.on_message = callBackOnMessage
		mqttClient.connect(BROKER_IP_ADDRESS)

def main():
    connected = False
    println("Trying to Connect to Server")
    connectToServer()
    mqttClient.loop_forever()



if __name__ == "__main__":
    main()