#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from helper.apptypes import RTapp
from helper.profgen import profileGenerator
import helper.profgen

import os

#check for environmental variables in case this app is started in a docker container
#MQTT Broker IP
if (os.environ.get('MQTT_BROKER_IP') != None):
    print("Environmental variable provided for MQTT_BROKER_IP: {0}".format(os.environ.get('MQTT_BROKER_IP')))
    MQTT_BROKER_IP = os.environ.get('MQTT_BROKER_IP')
else:
    MQTT_BROKER_IP = "localhost"
    print("No environmental variable provided for MQTT_BROKER_IP - using default: {0}".format(MQTT_BROKER_IP))

#MQTT Broker port
if (os.environ.get('MQTT_BROKER_PORT') != None):
    print("Environmental variable provided for MQTT_BROKER_PORT: {0}".format(os.environ.get('MQTT_BROKER_PORT')))
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT'))
else:
    MQTT_BROKER_PORT = 1883
    print("No environmental variable provided for MQTT_BROKER_IP - using default: {0}".format(MQTT_BROKER_IP))

MQTT_BROKER_KEEPALIVE = 60

#MQTT: the topic is formed of the app name: e.g. \Belt\command + JSON-string with all variable/values pairs
#OPC UA: the node name is formed of the app name: e.g. \Belt\command + .Variable name
TOPIC_COMMAND = "mosaiq.com.lenze.PyProfGen/command"
TOPIC_PARAMETER = "mosaiq.com.lenze.PyProfGen/parameter"
TOPIC_MONITOR = "mosaiq.com.lenze.PyProfGen/monitor"
TOPIC_PARAMETER_ON_CONNECT= "mosaiq.com.lenze.PyProfGen/parameteronconnect"

COMMAND_ID_MOVE_VELOCITY = "MC_MoveVelocity"
COMMAND_ID_MOVE_RELATIVE = "MC_MoveRelative"
COMMAND_ID_MOVE_STOP = "MC_MoveStop"
COMMAND_ID_NO_COMMAND = ""


async def cyclic(cycleTime):
    #APP initialization
    app = belt(cycleTime, "Belt")
    
    #enter cyclic execution
    while True:
        await asyncio.sleep(cycleTime)
        app.cyclic()
 
 
        
class belt(RTapp):
    "APP controlling the belt"
    def __init__(self, *args, **kwargs):
        #extend the parent class init function with app specific instance initialization
        super().__init__(*args, **kwargs)

        self.commandInterface = appCommandInterface()   
        self.parameter = appParameter()                 
        self.publicMonitorData = appPublicMonitorData() #all monitor data will be serialized and cyclically published
        
        #activate MQTT for this app (on connect publication need to be prepared __before__ so it can be sent out immediately on connect
        super().addOnConnectPublication(TOPIC_PARAMETER_ON_CONNECT, self.parameter)
        super().pubSubConnect(MQTT_BROKER_IP, MQTT_BROKER_PORT, MQTT_BROKER_KEEPALIVE)
        
        #register data for publishing
        super().addCyclicPublication(TOPIC_MONITOR, self.publicMonitorData)
        #received data of subscribed topic will be automatically mapped to the given data object: json-key = attribute name in instance, json-value = attribute value
        super().addSubscription(TOPIC_COMMAND, self.commandInterface)
        super().addSubscription( TOPIC_PARAMETER, self.parameter)

        self.profGenMovement = profileGenerator()
        

    def cyclic(self):
        super().cyclic()     #execute also code of cyclic method from parent class RTapp

        #command interface
        if (self.commandInterface.command == COMMAND_ID_MOVE_STOP):
            self.commandInterface.command = COMMAND_ID_NO_COMMAND
            self.profGenMovement.cmdStop = True
        
        elif (self.commandInterface.command == COMMAND_ID_MOVE_RELATIVE):
            self.commandInterface.command = COMMAND_ID_NO_COMMAND
            #initialize(aMax, vMax, sMin, sMax, vAct, vSet, sAct, sSet, moveType)
            self.profGenMovement.initialize(self.parameter.setAcceleration, 
                                            self.parameter.maxVelocity, 
                                            self.parameter.minPosition, 
                                            self.parameter.maxPosition, 
                                            self.publicMonitorData.actVelocity, 
                                            self.parameter.setVelocity, 
                                            self.publicMonitorData.actPosition,
                                            self.parameter.setDistance,
                                            helper.profgen.MOVE_TYPE_POSITION)

        elif (self.commandInterface.command == COMMAND_ID_MOVE_VELOCITY):
            self.commandInterface.command = COMMAND_ID_NO_COMMAND
            #initialize(aMax, vMax, sMin, sMax, vAct, vSet, sAct, sSet, moveType)
            self.profGenMovement.initialize(self.parameter.setAcceleration, 
                                            self.parameter.maxVelocity, 
                                            self.parameter.minPosition, 
                                            self.parameter.maxPosition, 
                                            self.publicMonitorData.actVelocity, 
                                            self.parameter.setVelocity, 
                                            self.publicMonitorData.actPosition,
                                            self.parameter.setDistance,
                                            helper.profgen.MOVE_TYPE_VELOCITY)

        #execute profile generator
        self.profGenMovement.update()

        #update public data which will be then sent via MQTT to subscribers
        self.publicMonitorData.actPosition = self.profGenMovement.sProf
        self.publicMonitorData.actVelocity = self.profGenMovement.vProf


class appCommandInterface():
    def __init__(self):
        self.command = ""
        
class appParameter():
    def __init__(self):
        self.setDistance = 0
        self.setVelocity = 300
        self.setAcceleration = 100
        self.maxPosition =1000000000
        self.minPosition = -self.maxPosition
        self.maxVelocity = 500
        self.maxAccleration = 1000.0
        
class appPublicMonitorData():
    def __init__(self):
        self.actVelocity = 0
        self.actPosition = 0