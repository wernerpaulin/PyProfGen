#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
from collections import namedtuple
import paho.mqtt.client as mqtt 
import time
#sudo pip3 install paho-mqtt
#sudo apt-get install -y mosquitto mosquitto-clients
#sudo systemctl enable mosquitto.service

MQTT_ERR_SUCCESS = 0

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
        self.mqttClient.on_connect = PubSub_onConnect
        self.mqttClient.on_message = PubSub_onMessage

        #connect to broker without exception in case the broker is not yet available or the network is not yet up
        self.mqttSaveConnect()
        #once the connected start the receive and send loop 
        self.mqttClient.loop_start()    #non-blocking call with automatic reconnects

    def mqttSaveConnect(self):
        try:
            self.mqttClient.connect(self.brokerIP, self.brokerPort, self.brokerKeepalive)
        except Exception as e:
            print("MQTT: Fundamental error: {0}".format(e))
            print("MQTT: Trying to connect...")
            time.sleep(1)
            self.mqttSaveConnect()


    def addSubscription(self, topic, destinationDataObj):
        #MQTT
        self.subscriptionList[topic] = destinationDataObj   #register topic and the destination data object to which all receive data will be mapped
        
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

    
    #when the client connects to the broker (again), send all parameters out to initialize the UI and also subscribe to topics
    def onMqttBrokerConnected(self):
        print("MQTT: RT App <{0}> connected to broker at: <{1}>".format(self.appName, self.brokerIP))    #this print() is necessary so that the following code is executed - no idea why?

        #send parameters for subscribers to initalize their default data e.g. in UI
        try:
            print("MQTT: publishing all parameters of RT App <{0}> for subscribes to initalize their default data e.g. in UI".format(self.appName))    
            for topic in self.publicationListOnConnect:
                try:
                    sourceDataObj = self.publicationListOnConnect[topic]
                    self.mqttClient.publish(topic, json.dumps(sourceDataObj.__dict__))
        
                except Exception as e:
                    print("MQTT: Error publishing topic <{0}>: {1}".format(topic, e))
        except Exception as e:
            print("MQTT: Error publishing topic: <{0}>".format(e))

        #subscribe to all topics the app wants to consume
        try:
            print("MQTT: subsribing to all topics the RT App <{0}> wants to consume".format(self.appName))    
            for topic in self.subscriptionList:
                try:
                    retSubscribe, mid = self.mqttClient.subscribe(topic)        #mid ...message id
                    if (retSubscribe != MQTT_ERR_SUCCESS):
                        print("MQTT: Bad return code when subscribing to topic <{0}>: {1}".format(topic, retSubscribe))
                        break

                except Exception as e:
                    print("MQTT: Error subscribing to topic <{0}>: {1}".format(topic, e))
            
            #subscription failed -> try again
            if (retSubscribe != MQTT_ERR_SUCCESS):
                print("MQTT: Trying to subscribe again...")
                time.sleep(1)
                self.onMqttBrokerConnected()

            
        except Exception as e:
            print("MQTT: Error subscribing to topic: <{0}>".format(e))

    #when the UI connects to the broker send onConnect values to allow the UI to (re-)initalize itself
    def onUserInterfaceConnected(self):
        print("MQTT: UI requests a publish of on-connect parameters of RT App <{0}>".format(self.appName))

        #send parameters for subscribees to initalize their default data e.g. in UI
        try:
            print("MQTT: publishing all parameters of RT App <{0}> for subscribes to initalize their default data e.g. in UI".format(self.appName))    
            for topic in self.publicationListOnConnect:
                try:
                    sourceDataObj = self.publicationListOnConnect[topic]
                    self.mqttClient.publish(topic, json.dumps(sourceDataObj.__dict__))
        
                except Exception as e:
                    print("MQTT: Error publishing topic <{0}>: {1}".format(topic, e))
        except Exception as e:
            print("MQTT: Error publishing topic: <{0}>".format(e))

