##################################################################################################
# Script to read telegram from Landis&Gyr Ultraheat UH50 (T550)                                  #
#                                                                                                #
# This script sends the kWh and m3 values to Home Assistant in JSON format                       #
# Exact Home Assistant configuration to be given                                                 #
#                                                                                                #
# Source:                                                                                        #
# Script from Magnat in https://gathering.tweakers.net/forum/list_messages/1535019               #
#                                                                                                #
# Requirement: Python3, BlockingScheduler                                                        #
##################################################################################################

import serial
import re
import requests
from time import sleep
import json
from apscheduler.schedulers.blocking import BlockingScheduler
import pickle
import datetime
import time
import os
import schedule

os.environ['TZ'] = 'Europe/Stockholm'

scheduler = BlockingScheduler()


# Only run first time:
#store = "0"
#pickle.dump( store, open( "lastkwhvalue.p", "wb" ) )
#pickle.dump( store, open( "lastkwh.p", "wb" ) )
#pickle.dump( store, open( "lastm3value.p", "wb" ) )
#pickle.dump( store, open( "lastm3.p", "wb" ) )

@scheduler.scheduled_job('cron', hour=0, minute=1, timezone='Europe/Stockholm')
def resetValue():
    reset = "0"
    pickle.dump( reset, open( "lastkwh.p", "wb" ) )
    pickle.dump( reset, open( "lastm3.p", "wb" ) )
    print("Values set to 0")

@scheduler.scheduled_job('cron', hour='0-23', timezone='Europe/Stockholm')
def getData():

    conn = serial.Serial('/dev/ttyUSB0',
                     baudrate=300,
                     bytesize=serial.SEVENBITS,
                     parity=serial.PARITY_EVEN,
                     stopbits=serial.STOPBITS_TWO,
                     timeout=1,
                     xonxoff=0,
                     rtscts=0
                     )

    # Wake up
    conn.setRTS(False)
    conn.setDTR(False)
    sleep(5)
    conn.setDTR(True)
    conn.setRTS(True)

    # send /?!
    conn.write(str.encode("\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A"))

    # Read at 300 BAUD, typenr
    print(conn.readline())
    print(conn.readline())

    # Read at 2400 BAUD, higher might be possible
    conn.baudrate=2400

    # Read 18 lines (the size of the telegram)
    counter = 0
    try:
        while counter < 18:
            line=conn.readline().decode('utf-8')
            print(line)

            # This will match on the first line of the telegram with GJ and m3 values.
            matchObj = re.match(r".+6\.8\(([0-9]{4}\.[0-9]{3})\*MWh\)6\.26\(([0-9]{5}\.[0-9]{2})\*m3\)9\.21\(([0-9]{8})\).+", line, re.I|re.S)
            if matchObj:
                kwhValue=round(float(matchObj.group(1)) * 1000)
                m3Value=round(float(matchObj.group(2)) * 1000)
                print("kWh: " + str(kwhValue))
                print("m3: " + str(m3Value))

                # -- Kwh calc start --
                oldKwhValue = pickle.load( open( "lastkwhvalue.p", "rb" ) ) # Varibel/Value stored in *.p
                oldKwh = pickle.load( open( "lastkwh.p", "rb" ) )

                kwhDiff = int(kwhValue) - int(oldKwhValue)

                newKwh = int(kwhDiff) + int(oldKwh)

                pickle.dump( kwhValue, open( "lastkwhvalue.p", "wb" ) )
                pickle.dump( newKwh, open( "lastkwh.p", "wb" ) )
                # -- Kwh calc end --

                # -- m3 calc start --
                oldM3Value = pickle.load( open( "lastm3value.p", "rb" ) )
                oldM3 = pickle.load( open( "lastm3.p", "rb" ) )

                m3Diff = int(m3Value) - int(oldM3Value)

                newM3 = int(m3Diff) + int(oldM3)

                pickle.dump( m3Value, open( "lastm3value.p", "wb" ) )
                pickle.dump( newM3, open( "lastm3.p", "wb" ) )
                # -- m3 calc end --

                # Json to Home Assistant
                url = 'http://192.168.X.X:8123/api/webhook/fjarrvarme'
                myobj = {'kwh': newKwh, 'm3': newM3}

                x = requests.post(url, json = myobj)

                print(json.dumps({"kWh": newKwh, "m3": newM3}))
                break

            counter = counter + 1

    finally:
        conn.close()
        print("Read done")

#scheduler.add_job(getData, 'interval', seconds=20) # Only for test 20 seconds interval
scheduler.start()
