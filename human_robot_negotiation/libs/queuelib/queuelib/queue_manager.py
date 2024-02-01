import time
import traceback

import pika

host = 'localhost'
credentials = pika.PlainCredentials("orchestrator", "orchestrator")


class MultiQueueHandler:
    _instance = None

    connection: pika.BlockingConnection
    is_connected: bool
    queues: list[str]

    def __new__(cls, queues=None, port=5672):
        if queues is None:
            queues = []

        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.connection_params = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=credentials
            )
            cls._instance.connection = None
            cls._instance.channel = None
            cls._instance.is_connected = False
            cls._instance.queues = queues

            cls._instance.connect()

        return cls._instance


    def connect(self):
        if not self.is_connected:
            try:
                self.connection = pika.BlockingConnection(self.connection_params)
                self.channel = self.connection.channel()
                self.is_connected = True
                print("Connection is successful.")
            except Exception as e:
                print(f"Error connecting to RabbitMQ: {e}")
                print(traceback.format_exc())

    def disconnect(self):
        if self.is_connected:
            self.connection.close()
            self.is_connected = False
            print("Disconnected from RabbitMQ.")

    def consume_all_queues_with_callback(self, callback):
        try:
            for queue_name in self.queues:
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.basic_consume(queue_name, callback, auto_ack=True)

            self.channel.start_consuming()
        except Exception as e:
            print(traceback.format_exc())

    def wait_for_message_from_queue(self, queue_name):
        method_frame, header_frame, body = self.channel.basic_get(queue_name)

        while not method_frame:
            time.sleep(1)

        return body

    def send_message(self, queue_name, message):
        if self.connection and self.connection.is_open:
            try:
                # Send the message to the specified queue
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                    )
                )

                print(f"Message sent to queue '{queue_name}': {message}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("Not connected to RabbitMQ. Call 'connect()' first.")


