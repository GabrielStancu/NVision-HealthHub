import serial
import pymongo
import datetime
import pika
import json

serialNumber = 'ec34a3b7-2b5e-4255-a143-9b8b207756d2'
refTimestamp = datetime.datetime.now()
refMillis = 0
dbClient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbClient["healthDb"]
measurementsCollection = db["measurements"]

def storeData(type, value, timestamp):
    measurementsCollection.insert_one({'type': type, 'value': value, 'sent': False, 'timestamp': timestamp})

def getMeasurementTime(relMillis):
    global refMillis
    global refTimestamp
    if (refMillis == 0):
        refMillis = relMillis
        refTimestamp = datetime.datetime.now()

    relTime = relMillis - refMillis
    timestamp = refTimestamp + datetime.timedelta(milliseconds=relTime)
    return timestamp

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def sendNotSentData():
    unsentQuery = { "sent": False }
    updateQuery = { "$set": { "sent": True } }
    unsentData = measurementsCollection.find(unsentQuery)

    url = 'amqps://jchjxvxx:ZM0XdOye65LJHaVRPg-xA_o_mlexMRxP@cow.rmq2.cloudamqp.com/jchjxvxx'
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel() 
    channel.queue_declare(queue='healthHubQueue', durable=True) 
    for unsentRecord in unsentData: 
        try:
            serializedMessage = json.dumps({ 'type': unsentRecord['type'], 'value': unsentRecord['value'], 'timestamp': unsentRecord['timestamp'], 'deviceSerial': serialNumber}, default = myconverter)
            channel.basic_publish(exchange='',
                        routing_key='healthHubQueue',
                        body=serializedMessage)
            measurementsCollection.update_one(unsentQuery, updateQuery)
        except Exception as e:
            print('Error RabbitMQ: '+ str(e))

    connection.close()

def alertAnomaly():
    a = 0

def checkAnomalies():
    a = 0

ser = serial.Serial('/dev/ttyACM0',9600)

while True:
    line = ser.readline()
    print('Received line: ' + line)

    parts = line.split(";")
    type = parts[0]
    value = float(parts[1])
    measurementMillis = float(parts[2])
    timestamp = getMeasurementTime(measurementMillis)

    storeData(type, value, timestamp)
    checkAnomalies()
    sendNotSentData()
    # measurementsCollection.remove()
    # print(measurementsCollection.count())
