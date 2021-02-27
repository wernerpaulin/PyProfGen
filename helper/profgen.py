#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math

MOVE_TYPE_POSITION = 1
MOVE_TYPE_VELOCITY = 2


class profileGenerator:
    "Generates position and velocity profile without feedback"
    #init
    def __init__(self):
        #inputs        
        self.aMax = 0
        self.vMax = 0
        self.sMin = 0
        self.sMax = 0
        self.vAct = 0
        self.vSet = 0
        self.sAct = 0
        self.sSet = 0
        self.moveType = 0

        #outputs
        self.sProf = 0
        self.vProf = 0

        #status
        self.inPos = False      #triggers profile generation in update function
        self.initDone = False
        self.cmdStop = False
        self.vMaxReached = False

        #internal data
        self.lastCallTime = 0
        self.samplingTime = 0
        self.dir = 1
        return
    
    def initialize(self, aMax, vMax, sMin, sMax, vAct, vSet, sAct, sSet, moveType):
        #inputs        
        self.aMax = aMax
        self.vMax = vMax
        self.sMin = sMin
        self.sMax = sMax
        self.vAct = vAct
        self.vSet = vSet
        self.sAct = sAct
        self.sSet = max(min(sSet, sMax), sMin)
        self.moveType = moveType

        #outputs
        self.sProf = sAct
        self.vProf = vAct

        #status
        self.inPos = False      #triggers profile generation in update function
        self.initDone = True
        self.cmdStop = False
        self.vMaxReached = False

        #internal data
        self.lastCallTime = time.time()
        self.samplingTime = 0
        if (self.moveType == MOVE_TYPE_POSITION):
            self.dir = 1 if sSet > sAct else -1
        elif (self.moveType == MOVE_TYPE_VELOCITY):
            self.dir = 1 if vSet > vAct else -1
        else:
            self.dir = 1
        return

    def update(self):
        #do not proceed until init has been done
        if (self.initDone == False): return

        #cycle time calculation
        self.samplingTime = max(time.time() - self.lastCallTime, 0)
        self.lastCallTime = time.time()
       
        #generate s/v profile depending on elapsed time (no feedback)
        try:
            #position control: full trapezoid profile generation with dynamic stop ramp
            if (self.moveType == MOVE_TYPE_POSITION):
                if (self.inPos == False):
                    #if not stop command pending ramp up to maximum speed, otherwise down to 0
                    if (self.cmdStop == False):
                        #ramp up velocity as integral of acceleration, limited by maximum acceleration
                        self.vProf = self.vProf + self.aMax * self.samplingTime * self.dir

                        #limit to set velocity
                        if self.dir >= 0:
                            self.vProf = min(self.vProf, self.vSet)
                            #limit to maximum velocity
                            self.vProf = min(max(self.vProf, 0), self.vMax) 
                        else:
                            self.vProf = max(self.vProf, -self.vSet)
                            #limit to maximum velocity
                            self.vProf = min(max(self.vProf, -self.vMax), 0) 

                    else:
                        #stop requested: reduce to velocity until standstill
                        self.vProf = self.vProf - self.aMax * self.samplingTime * self.dir
                        
                        #limit velocity to 0
                        if self.dir >= 0:
                            self.vProf = max(self.vProf, 0)     #vProf is approaching 0 from positive towards 0 - avoid becoming negative
                        else:
                            self.vProf = min(self.vProf, 0)     #vProf is approaching 0 from negative towards 0 - avoid becoming positive
                    
                        #check if standstill has been reached -> end profile generation
                        if self.vProf == 0:
                            self.endOfProfile()
    
                    #check for breaking point when deceleration need to kick in to reach set position
                    #s = v*t/2 (necessary distance to break with current velocity) => v = 2*s/t (t depends on deceleration ramp)  
                    #v=a*t => t = v/a (this is the time necessary the velocity increases/decreases with constant acceleration
                    #v = 2*s/(v/a)
                    sRemaining = abs(self.sSet - self.sProf)
                    if (self.vProf != 0) and (self.aMax != 0):
                        vMaxBreaking = 2.0 * sRemaining / (self.vProf / self.aMax)
                    else:
                        vMaxBreaking = self.vProf

                        
                    #limit vSet to be able to stop at sSet
                    if self.dir >= 0:
                        self.vProf = min(self.vProf, vMaxBreaking)
                    else:
                        self.vProf = max(self.vProf, vMaxBreaking)
                    
                    #generate set position by integral of current velocity
                    self.sProf = self.sProf + self.vProf * self.samplingTime
        
                    #check if target positions has been reached in positive and negative direction
                    if self.dir >= 0:
                        if (self.sProf >= self.sSet):
                            self.endOfProfile()
                    else:
                        if (self.sProf <= self.sSet):
                            self.endOfProfile()
            
            #velocity control: no position limits
            elif (self.moveType == MOVE_TYPE_VELOCITY):
                #inPos is only set in case vProf reaches 0 after a stop command
                if (self.inPos == False):
                    #if not stop command pending ramp up to maximum speed, otherwise down to 0
                    if (self.cmdStop == False):
                        #ramp up velocity as integral of acceleration, limited by maximum acceleration
                        self.vProf = self.vProf + self.aMax * self.samplingTime * self.dir
    
                        #limit to set speed in all 4 quadrants: pos/neg velocity and pos/neg direction
                        if self.dir >= 0:
                            self.vProf = min(self.vProf, self.vSet)
                        else:
                            self.vProf = max(self.vProf, self.vSet)      
    
                        #limit to maximum velocity
                        self.vProf = min(max(self.vProf, -self.vMax), self.vMax) 
                    else:
                        #stop requested: reduce to velocity until standstill
                        self.vProf = self.vProf - self.aMax * self.samplingTime * self.dir
    
                        #limit velocity to 0
                        if self.dir >= 0:
                            self.vProf = max(self.vProf, 0)     #vProf is approaching 0 from positive towards 0 - avoid becoming negative
                        else:
                            self.vProf = min(self.vProf, 0)     #vProf is approaching 0 from negative towards 0 - avoid becoming positive
    
                        if self.dir >= 0:
                            if (self.vProf >= self.vMax):
                                self.vMaxReached = True
                        else:
                            if (self.vProf <= self.vMax):
                                self.vMaxReached = True

                        #check if standstill has been reached -> end profile generation
                        if self.vProf == 0:
                            self.endOfProfile()
                    
    
                    #generate set position by integral of current velocity
                    self.sProf = self.sProf + self.vProf * self.samplingTime
            else:
                return
            
                        
        #catch exception like div by zero,...
        except Exception as e:
            self.endOfProfile()
            print("Movement Profile Generator Update failed: {0}".format(e))

        return
    
    def endOfProfile(self):
        #in case of stop, do not touch sSet: profiles stops depending on ramp down. Otherwise set sSet to target position
        if self.cmdStop == False:
            self.sProf = self.sSet
        
        self.cmdStop = False
        self.inPos = True
        self.vProf = 0
        
        