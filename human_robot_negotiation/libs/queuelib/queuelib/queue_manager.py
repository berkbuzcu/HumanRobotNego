import json
import time
import traceback
import uuid
import pika

host = 'rabbitmq'
credentials = pika.PlainCredentials("orchestrator", "orchestrator")


def prep_init_message(name, error=None):
    return json.dumps({
        "from": name,
        "status": "success",
        "error": error,
        "type": "init_lifecheck"
    })


class MultiQueueHandler:
    _instance = None

    connection: pika.BlockingConnection
    is_connected: bool
    queues: list[str]
    correlation_id: str

    def __new__(cls, queues=None, port=5672, correlation_id=None):
        if queues is None:
            queues = []

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

    def consume_all_queues_with_callback(self, callback):
        try:
            for queue_name in self.queues:
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.channel.basic_consume(queue_name, callback, auto_ack=False)

            self.channel.start_consuming()
        except Exception as e:
            print(traceback.format_exc())

    def wait_for_message_from_queue(self, queue_name):
        method_frame, header_frame, body = self.channel.basic_get(queue_name)

        while True:
            print(method_frame, header_frame, body)

            if method_frame:
                print(self.correlation_id, "---", header_frame.correlation_id)

                if header_frame.correlation_id == self.correlation_id:
                    print("Message is from myself, ignoring.")
                else: break
            else:
                print("No message in queue, waiting.")

            time.sleep(1)
            method_frame, header_frame, body = self.channel.basic_get(queue_name)

        return json.loads(body)

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
                        correlation_id=self.correlation_id
                    )
                )

                print(f"Message sent to queue '{queue_name}': {message}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("Not connected to RabbitMQ. Call 'connect()' first.")
