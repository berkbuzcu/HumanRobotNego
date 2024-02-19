# Python 2.7 compatibility imports
from __future__ import print_function

import time
import traceback
import json
import pika

host = 'rabbitmq'
credentials = pika.PlainCredentials("orchestrator", "orchestrator")


class RobotMessage(object):
    def __init__(self,sender, payload, status, context="robot", queue_type="robot"):
        self.sender = sender
        self.payload = payload
        self.context = context
        self.status = status
        self.queue_type = queue_type

    def to_json(self):
        return json.dumps({
            "sender": self.sender,
            "payload": self.payload,
            "context": self.context,
            "status": self.status,
            "queue_type": self.queue_type
        })

def prep_init_message(name, error=None):
    message_dict = {
        "sender": name,
        "status": "true",
        "payload": {"error": error},
        "context": "robot",
        "queue_type": "robot"
    }
    return RobotMessage(**message_dict)



class MultiQueueHandler(object):
    _instance = None

    def __new__(cls, queues=None, host='rabbitmq', port=5672, correlation_id="nao"):
        if queues is None:
            queues = []

        if type(queues) != list:
            queues = list(queues)

        if cls._instance is None:
            cls._instance = super(MultiQueueHandler, cls).__new__(cls)

            print("Connecting to: ", host, port)

            cls._instance.connection_params = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials
            )
            cls._instance.connection = None
            cls._instance.channel = None
            cls._instance.is_connected = False
            cls._instance.queues = queues
            cls._instance.correlation_id = correlation_id

            cls._instance.connect()

        return cls._instance

    def connect(self):
        if not self.is_connected:
            try:
                self.connection = pika.BlockingConnection(self.connection_params)
                self.channel = self.connection.channel()
                self.is_connected = True
                print("Connection is successful.")

                for queue in self.queues:
                    self.channel.queue_declare(queue=queue, durable=True)

            except Exception as e:
                print("Error connecting to RabbitMQ: {}".format(e))
                print(traceback.format_exc())
                print("Retrying RabbitMQ Connection...")
                self.connect()

    def disconnect(self):
        if self.is_connected:
            self.connection.close()
            self.is_connected = False
            print("Disconnected from RabbitMQ.")

    @staticmethod
    def __wrap_message(message_json):
        return RobotMessage(**message_json)

    def wait_for_message_from_queue(self, queue_name="robot"):
        method_frame, header_frame, body = self.channel.basic_get(queue_name)

        while True:
            if method_frame:
                if header_frame.correlation_id == self.correlation_id:
                    print("Message is from myself, ignoring.")
                else:
                    break
            else:
                print("No message in queue, waiting.")

            time.sleep(1)
            method_frame, header_frame, body = self.channel.basic_get(queue_name)
        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        print("Message received from queue: ", queue_name)
        return self.__wrap_message(json.loads(body))

    def send_message(self, message):
        if self.connection and self.connection.is_open:
            try:
                # Send the message to the specified queue
                self.channel.basic_publish(
                    exchange='',
                    routing_key=message.queue_type,  # Assuming queue_type is an attribute of the message instance
                    body=message.to_json(),
                    properties=pika.BasicProperties(
                        correlation_id=self.correlation_id
                    )
                )

                print("Message sent to queue '{}': {}".format(message.queue_type, message))
            except Exception as e:
                traceback.print_exc()
                print("Error sending message: {}".format(e))
        else:
            print("Not connected to RabbitMQ. Call 'connect()' first.")

