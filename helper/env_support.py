#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def initializeENV(envName, defaultValue):
    envNameValue = os.environ.get(envName)

    #if given return value otherwise apply default value
    if (envNameValue != None):
        print("Environmental variable <{0}> is set to: {1}".format(envName, envNameValue))
        return envNameValue
    else:
        print("Environmental variable <{0}> was not given. Default value <{1}> applies".format(envName, defaultValue))
        return defaultValue
    