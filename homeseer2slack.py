#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
from urllib import request, parse
import json


mqttBroker = "mqtt.lan"
mqttPort = 1883
mqttUser = ""
mqttPass = "" 

mqttClient = mqtt.Client()

# Posting to a Slack channel
def sendSlackMsg(text):
    post = {"text": "{0}".format(text)}

    try:
        json_data = json.dumps(post)
        req = request.Request("https://hooks.slack.com/services/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",
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'}) 
        resp = request.urlopen(req)
    except Exception as em:
        print("EXCEPTION: " + str(em))

def onMessage(client, userdata, msg):
    payload = (msg.payload).decode("utf-8") 
    print(msg.topic + " " + payload)
    sendSlackMsg(payload)

def onConnect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    mqttClient.subscribe("hs_slack")

def onDisconnect(client, userdata, result):
    print("Disconnected because: " + result + "... Attempting to reconnect")
    mqttClient.reconnect()


mqttClient.on_connect = onConnect
mqttClient.on_message = onMessage
mqttClient.on_disconnect = onDisconnect
mqttClient.connect(mqttBroker, mqttPort, 60)

mqttClient.loop_forever()

