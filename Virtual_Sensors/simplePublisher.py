import paho.mqtt.client as PahoMQTT
import time
import pandas as pd
import json

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
	'BLOCK1:BEDROOM:Zone Operative Temperature [C](Hourly:ON)':'Zone_bedroom:Temp_Op', #AP
	'BLOCK1:BATHROOM:Zone Operative Temperature [C](Hourly:ON)':'Zone_bathroom:Temp_Op',
	'BLOCK1:KITCHEN:Zone Operative Temperature [C](Hourly:ON)':'Zone_kitchen:Temp_Op', #AT

	'BLOCK1:BEDROOM:Zone Ventilation Air Change Rate [ach](Hourly)':'Zone_bedroom:Ventilation',

    #Zone Mean Air Temperature
    'BLOCK1:BEDROOM:Zone Mean Air Temperature [C](Hourly:ON)':'Zone_bedroom:Temp_mean', #AP
	'BLOCK1:BATHROOM:Zone Mean Air Temperature [C](Hourly:ON)':'Zone_bathroom:Temp_mean',
	'BLOCK1:KITCHEN:Zone Mean Air Temperature [C](Hourly:ON)':'Zone_kitchen:Temp_mean', #AT # AS


    'Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)':'Outdoor:Temp',
    'Environment:Site Outdoor Air Barometric Pressure [Pa](Hourly)':'Outdoor:Pressure',
    'Environment:Site Wind Speed [m/s](Hourly)':'Wind',
	'Environment:Site Wind Direction [deg](Hourly)':'Wind_direction',


    'BLOCK1:BEDROOM:Zone Windows Total Transmitted Solar Radiation Rate [W](Hourly)':'Zone_bedroom:SolarRadiationRate',  #AI
	'BLOCK1:BATHROOM:Zone Windows Total Transmitted Solar Radiation Rate [W](Hourly)':'Zone_bathroom:SolarRadiationRate',
	'BLOCK1:KITCHEN:Zone Windows Total Transmitted Solar Radiation Rate [W](Hourly)':'Zone_kitchen:SolarRadiationRate',

    'BLOCK1:BEDROOM:Zone Air Relative Humidity [%](Hourly:ON) ':'Zone_bedroom:Humidity',
	'BLOCK1:BATHROOM:Zone Air Relative Humidity [%](Hourly:ON)':'Zone_bathroom:Humidity',
	'BLOCK1:KITCHEN:Zone Air Relative Humidity [%](Hourly:ON)':'Zone_kitchen:Humidity',

    'DistrictCooling:Facility [J](Hourly)':'Cool',

    'Electricity:Facility [J](TimeStep)':'Power'
}




if __name__ == "__main__":
	test = MyPublisher("MyPublisher")
	test.start()
	df=pd.read_csv('data.csv',sep=',',decimal=',',index_col=0)
	df.index=pd.to_datetime(df.index,unit='s')
	GATEWAY_NAME="VirtualBuilding"
	for i in df.index:
		for j in df.loc[i].items():
			nodeID=j[0]
			value=j[1]
			if nodeID=='Power':
				measurement="Power"
			else:
				measurement="Temperature"
			payload={
						"location":str(GATEWAY_NAME),
						"measurement":measurement,
						"node":str(nodeID),
						"time_stamp":str(i),
						"value":value}
			test.myPublish ('ict4bd', json.dumps(payload))
			time.sleep(0.1)

	test.stop()


