import paho.mqtt.client as PahoMQTT
import time
import pandas as pd
import json
from datetime import datetime
class MyPublisher:
	def __init__(self, clientID):
		self.clientID = clientID
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self.messageBroker = 'localhost'

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()

	def stop (self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, topic, message):
		# publish a message with a certain topic
		self._paho_mqtt.publish(topic, message, 2)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))


meas = {
	'BLOCK1:BEDROOM:Zone Operative Temperature [C](TimeStep:ON)':'Zone_bedroom:Temp_Op', #AP
	'BLOCK1:BATHROOM:Zone Operative Temperature [C](TimeStep:ON)':'Zone_bathroom:Temp_Op',
	'BLOCK1:KITCHEN:Zone Operative Temperature [C](TimeStep:ON)':'Zone_kitchen:Temp_Op', #AT

	'BLOCK1:BEDROOM:Zone Ventilation Air Change Rate [ach](TimeStep)':'Zone_bedroom:Ventilation',

    #Zone Mean Air Temperature
    'BLOCK1:BEDROOM:Zone Mean Air Temperature [C](TimeStep:ON)':'Zone_bedroom:Temp_mean', #AP
	'BLOCK1:BATHROOM:Zone Mean Air Temperature [C](TimeStep:ON)':'Zone_bathroom:Temp_mean',
	'BLOCK1:KITCHEN:Zone Mean Air Temperature [C](TimeStep:ON)':'Zone_kitchen:Temp_mean', #AT # AS


    'Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)':'Outdoor:Temp',
    'Environment:Site Outdoor Air Barometric Pressure [Pa](TimeStep)':'Outdoor:Pressure',
    'Environment:Site Wind Speed [m/s](TimeStep)':'Wind',
	'Environment:Site Wind Direction [deg](TimeStep)':'Wind_direction',


    'BLOCK1:BEDROOM:Zone Windows Total Transmitted Solar Radiation Rate [W](TimeStep)':'Zone_bedroom:SolarRadiationRate',  #AI
	'BLOCK1:BATHROOM:Zone Windows Total Transmitted Solar Radiation Rate [W](TimeStep)':'Zone_bathroom:SeolarRadiationRate',
	'BLOCK1:KITCHEN:Zone Windows Total Transmitted Solar Radiation Rate [W](TimeStep)':'Zone_kitchen:SolarRadiationRate',

    'BLOCK1:BEDROOM:Zone Air Relative Humidity [%](TimeStep:ON)':'Zone_bedroom:Humidity',
	'BLOCK1:BATHROOM:Zone Air Relative Humidity [%](TimeStep:ON)':'Zone_bathroom:Humidity',
	'BLOCK1:KITCHEN:Zone Air Relative Humidity [%](TimeStep:ON)':'Zone_kitchen:Humidity',

    'DistrictCooling:Facility [J](TimeStep)':'Cool',

    'Electricity:Facility [J](TimeStep)':'Power'
}


pub = MyPublisher("MyPublisher")
pub.start()
df=pd.read_csv('eplusout_3.csv',sep=',',decimal=',',index_col=0)

GATEWAY_NAME="VirtualBuilding"
x=input("START?")
count=0
dataPerMonth = 24*31*6
print(len(df.index))
for i in range(len(df.index)):

    if i-24*31*6*3> dataPerMonth:

        break

    tt = df.index[i]
    x, hours = tt.split('  ')
    month,days = x.split('/')
    month='02'
    tt = f'{month}/{days}/2021{hours}'
    tt = tt.replace(' ', '')
    if '202124:' in tt:
        tt=tt.replace('24:', '00:')
        timestamp = time.mktime(datetime.strptime(tt, "%m/%d/%Y%H:%M:%S").timetuple())
        timestamp += 86400
    else:
        timestamp = time.mktime(datetime.strptime(tt, "%m/%d/%Y%H:%M:%S").timetuple())

    for key, val in meas.items():
        if 'District' in key or 'Electricity' in key:
            new_val = float(df[key][i])/3.6e6
        elif 'Pressure' in key:
            new_val = float(df[key][i])/1000
        else:
            new_val = float(df[key][i])
        payload={
            "location":str(GATEWAY_NAME),
            "measurement":val,
            #"time_stamp":datetime.utcnow().isoformat(),
            "time_stamp":int(timestamp),
            "value":new_val
        }
        print(payload)
        pub.myPublish ('ict4bd', json.dumps(payload))
        time.sleep(0.1)
pub.stop()
