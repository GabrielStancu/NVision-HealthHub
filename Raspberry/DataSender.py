import pika
import json

class DataSender:
    __url = 'amqps://jchjxvxx:ZM0XdOye65LJHaVRPg-xA_o_mlexMRxP@cow.rmq2.cloudamqp.com/jchjxvxx'

    def send_not_sent_data(self, unsent_data, serial_number):
        url = self.__url
        queue = 'measurements'

        for unsent_record in unsent_data:
            message = json.dumps({ 'type': unsent_record.type, 'value': unsent_record.value, 'timestamp': unsent_record.timestamp, 'deviceSerial': serial_number}) 
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