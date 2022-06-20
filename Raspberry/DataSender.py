import pika
import json
from datetime import datetime
from dateutil import tz

class DataSender:
    __url = 'amqps://jchjxvxx:ZM0XdOye65LJHaVRPg-xA_o_mlexMRxP@cow.rmq2.cloudamqp.com/jchjxvxx'

    def send_not_sent_data(self, unsent_data, serial_number):
        url = self.__url
        queue = 'measurements'
        documents = self.__recordsToDocuments(unsent_data)
        message = json.dumps({ 'records': documents, 'deviceSerial': serial_number}, 
                            indent=4, sort_keys=True, default=str) 
        print(message)
        self.__send(url, queue, message)       

    def __send(self, url, queue, message):
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel() 
        channel.queue_declare(queue=queue, durable=True) 
        
        try:
            channel.basic_publish(exchange='',
                        routing_key=queue,
                        body=message)
        except Exception as e:
            print('Error RabbitMQ: '+ str(e)) 

        connection.close()

    def __recordsToDocuments(self, records):
        documents = [None for _ in range(len(records))]     

        for (i, m) in enumerate(records):
            documents[i] = { 'type': m.type, 'value': m.value, 
                             'timestamp': self.__localToUtc(m.timestamp)}
        return documents

    def __localToUtc(self, date_str):
        from_zone = tz.tzlocal()
        to_zone = tz.tzutc()

        local = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        local = local.replace(tzinfo=from_zone)
        utc = local.astimezone(to_zone)
        utc_str = str(utc)
        
        return utc_str