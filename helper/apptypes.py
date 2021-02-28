#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
from collections import namedtuple
import paho.mqtt.client as mqtt 
#sudo pip3 install paho-mqtt
#sudo apt-get install -y mosquitto mosquitto-clients
#sudo systemctl enable mosquitto.service
#https://www.ev3dev.org/docs/tutorials/sending-and-receiving-messages-with-mqtt/
#http://www.steves-internet-guide.com/python-mqtt-publish-subscribe/
#open port 1883 in Windows: https://iot.stackexchange.com/questions/1093/how-to-modify-mosquittos-windows-firewall-inbound-rule-to-only-allow-connection
#https://pypi.org/project/paho-mqtt/#callbacks


def PubSub_onConnect(client, userdata, flags, rc):
    if (rc != 0):
        print("MQTT: Error connecting with result code {0}".format(rc))
    else:
        userdata.onMqttBrokerConnected()


def PubSub_onMessage(client, userdata, msg):
    #forward message to app instance in which the MQTT client lives  
    try:
        userdata.onMqttMessageReceived(msg.topic, msg.payload.decode())
    except Exception as e:
        print("MQTT: unhandled topic <{0}> received with payload {1} and error: {3}".format(msg.topic, msg.payload.decode(), e))



class RTapp:
    "Cyclic realtime app"
    def __init__(self, cycleTime, appName):
        self.cycleTime = cycleTime
        self.appName = appName
        self.mqttClient = {}
        self.brokerIP = ""
        self.brokerPort = 0
        self.brokerKeepalive = 0
        self.subscriptionList = dict()          #[topic] = data object
        self.publicationListCyclic = dict()     #[topic] = data object
        self.publicationListOnConnect = dict()  #[topic] = data object

        print("Init of RT app <{0}> done".format(self.appName))

    def cyclic(self):
        #walk through all topics registered for cyclic publishing
        for topic in self.publicationListCyclic:
            try:
                sourceDataObj = self.publicationListCyclic[topic]
                #self.subscriptionList[topic] ...source data instance its data need to be published
                #key                          ...name of attribute in instance
                #jsonObj[key]                 ...value to be read from attribute
                self.mqttClient.publish(topic, json.dumps(sourceDataObj.__dict__))
    
            except Exception as e:
                print("MQTT: Error publishing topic <{0}>: {2}".format(topic, e))

    def pubSubConnect(self, brokerIP, brokerPort, brokerKeepalive):
        print("MQTT: connecting to broker with IP address <{0}> via port {1}".format(brokerIP, brokerPort))

        #connect to MQTT broker
        self.brokerIP = brokerIP
        self.brokerPort = brokerPort
        self.brokerKeepalive = brokerKeepalive
        self.mqttClient = mqtt.Client(userdata=self)
        self.mqttClient.connect(self.brokerIP, self.brokerPort, self.brokerKeepalive)

        self.mqttClient.on_connect = PubSub_onConnect
        self.mqttClient.on_message = PubSub_onMessage
        
        self.mqttClient.loop_start()
    
    def addSubscription(self, topic, destinationDataObj):
        #MQTT
        self.subscriptionList[topic] = destinationDataObj   #register topic and the destination data object to which all receive data will be mapped
        self.mqttClient.subscribe(topic)                    #register topic at broker
        
    def addCyclicPublication(self, topic, sourceDataObj):
        #MQTT
        self.publicationListCyclic[topic] = sourceDataObj
        
    def addOnConnectPublication(self, topic, sourceDataObj):
        #MQTT
        self.publicationListOnConnect[topic] = sourceDataObj
    
    def onMqttMessageReceived(self, topic, payload):
        try:
            #print("MQTT: RT app <{0}> received topic <{1}> with payload {2}".format(self.appName, topic, payloadJSON))
            #assume data is sent as JSON string: "{"id":"MC_MoveVelocity"}"
            jsonObj = json.loads(payload)
            #map json key values directly to class instance
            for key in jsonObj:
                #self.subscriptionList[topic] ...destination data instance
                #key                          ...name of attribute in instance which should be written
                #jsonObj[key]                 ...value to be written to attribute in instance
                setattr(self.subscriptionList[topic], key, jsonObj[key])    


        except Exception as e:
            print("MQTT: Error decoding received MQTT payload of RT app <{0}>, error: {1}".format(self.appName, e))

    
    #usually overloaded by child instance. Defined here to avoid that code breaks during MQTT callback
    def onMqttBrokerConnected(self):
        print("MQTT: RT App <{0}> connected to broker at: <{1}>".format(self.appName, self.brokerIP))    #this print() is necessary so that the following code is executed - no idea why?
        try:
            #walk through all topics registered for cyclic publishing
            for topic in self.publicationListOnConnect:
                try:
                    sourceDataObj = self.publicationListOnConnect[topic]
                    self.mqttClient.publish(topic, json.dumps(sourceDataObj.__dict__))
        
                except Exception as e:
                    print("MQTT: Error publishing topic <{0}>: {1}".format(topic, e))
        except Exception as e:
            print("MQTT: Error publishing topic: <{0}>".format(e))


#python3 /home/pi/mosaiq4tw/main.py