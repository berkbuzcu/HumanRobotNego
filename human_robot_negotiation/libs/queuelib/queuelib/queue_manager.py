import json
import time
import traceback
import typing as t
import uuid
import pika
import functools
import threading

from queuelib.message import AbstractMessage
from queuelib.enums import HANTQueue

credentials = pika.PlainCredentials("orchestrator", "orchestrator")


def prep_init_message(name: str, module_type: HANTQueue, error: bool = None):
    message_dict = json.dumps({
        "sender": name,
        "status": "true",
        "payload": {"error": error},
        "context": "init",
        "queue_type": module_type.value
    })
    return AbstractMessage.from_json(message_dict)


class MultiQueueHandler:
    _instance = None

    connection: pika.BlockingConnection
    is_connected: bool
    queues: t.List[HANTQueue]
    correlation_id: str

    def __new__(cls, queues=None, host='rabbitmq', port=5672, correlation_id=None):
        if queues is None:
            queues = []

        if type(queues) != list:
            queues = list(queues)

        if cls._instance is None:
            cls._instance = super().__new__(cls)

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
            cls._instance.correlation_id = correlation_id if correlation_id else str(uuid.uuid4())

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
                    self.channel.queue_declare(queue=queue.value, durable=True)

            except Exception as e:
                print(f"Error connecting to RabbitMQ: {e}")
                print(traceback.format_exc())
                print("Retrying RabbitMQ Connection...")
                self.connect()

    def disconnect(self):
        if self.is_connected:
            self.connection.close()
            self.is_connected = False
            print("Disconnected from RabbitMQ.")

    @staticmethod
    def __wrap_message(message_json) -> AbstractMessage:
        return AbstractMessage.from_json(message_json)

    def __wrap_callback(self, ch, method, properties, body, callback):
        message: AbstractMessage = self.__wrap_message(body)
        return callback(ch, method, properties, message)

    def consume_all_queues_with_callback(self, callback):
        try:
            for queue_name in self.queues:
                callback_wrapped = functools.partial(self.__wrap_callback, callback=callback)
                self.channel.basic_consume(queue_name.value, callback_wrapped, auto_ack=True)

            self.channel.start_consuming()
        except Exception as e:
            print(traceback.format_exc())

    def wait_for_message_from_queue(self, queue_name: HANTQueue | str) -> AbstractMessage:
        if queue_name is HANTQueue:
            queue_name = queue_name.value

        elif queue_name not in HANTQueue and type(queue_name) is not str:
            raise ValueError("Queue name must be of type HANTQueue or str")

        method_frame, header_frame, body = self.channel.basic_get(queue_name.value)

        while True:
            if method_frame:
                if header_frame.correlation_id == self.correlation_id:
                    print("Message is from myself, ignoring.")
                    print(body)
                else:
                    break
            else:
                print("No message in queue, waiting.")

            time.sleep(1)
            method_frame, header_frame, body = self.channel.basic_get(queue_name.value)

        self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        print("Message received from queue: ", queue_name)
        return self.__wrap_message(body)

    def __wrap_parallel_callback(self, ch, method, properties, body, callback):
        message: AbstractMessage = self.__wrap_message(body)
        print("Received parallel message: ", message)
        ch.stop_consuming()
        return callback(ch, method, properties, message)

    def __thread_connection(self, queue_name, callback):
        print("Initiating parallel connection to queue: ", queue_name)
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()
        result = channel.queue_declare(queue_name, durable=True)

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True)

        channel.start_consuming()

    def non_blocking_message_from_queue(self, queue_name: HANTQueue | str, callback) -> None:
        callback_wrapped = functools.partial(self.__wrap_parallel_callback, callback=callback)
        threading.Thread(target=self.__thread_connection, args=(queue_name.value, callback_wrapped)).start()

    def get_message_from_queue(self, queue_name: HANTQueue | str) -> AbstractMessage:
        if queue_name is HANTQueue:
            queue_name = queue_name.value

        elif queue_name not in HANTQueue and type(queue_name) is not str:
            raise ValueError("Queue name must be of type HANTQueue or str")

        method_frame, header_frame, body = self.channel.basic_get(queue_name.value, auto_ack=True)

        return self.__wrap_message(body) if body else None

    def send_message(self, message: AbstractMessage) -> None:
        if not isinstance(message, AbstractMessage):
            raise ValueError("Message must be of type AbstractMessage")

        if self.connection and self.connection.is_open:
            try:
                # Send the message to the specified queue
                self.channel.basic_publish(
                    exchange='',
                    routing_key=message.queue_type.value,
                    body=message.to_json(),
                    properties=pika.BasicProperties(
                        correlation_id=self.correlation_id
                    )
                )

                print(f"Message sent to queue '{message.queue_type.value}': {message}")
            except Exception as e:
                traceback.print_exc()
                print(f"Error sending message: {e}")
        else:
            print("Not connected to RabbitMQ. Call 'connect()' first.")
