import pika
import json

class DataSender:
    def sendNotSentData(self, unsentData):
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
                self.measurementsCollection.update_one(unsentQuery, updateQuery)
            except Exception as e:
                print('Error RabbitMQ: '+ str(e))

        connection.close()
