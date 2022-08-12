#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import app.belt as belt
CYCLE_TIME_APP = 0.2


""" CYCLIC SYSTEM """
try:
    print("Starting app")
    """ START CYCLIC EXECUTION """
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(belt.cyclic(CYCLE_TIME_APP))
    loop.run_forever()

except Exception as e:
    print("Event loop failed: {0}".format(e))
    
finally:
    print("Event loop stopped")
    loop.close()

