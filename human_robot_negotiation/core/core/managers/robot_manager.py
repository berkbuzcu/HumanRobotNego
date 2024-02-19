import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from .abstract_manager import AbstractManager
from queuelib.message import RobotMessage


class RobotManager(AbstractManager):
    queue_manager: MultiQueueHandler

    ### Server Methods ###
    def send_init_robot(self, robot_name):
        reply = {
            "context": "server",
            "body": {"function": "init_robot", "message": robot_name.lower()},
        }
        #request_message = f"server;init_robot;{robot_name.lower()}"
        self.__send_message(reply)

    def send_stop_server(self):
        reply = {
            "context": "server",
            "body": {"function": "stop_server", "message": ""},
        }
        #request_message = "server;stop_server"
        self.__send_message(reply)

    ### Robot Methods ###
    def send_mood(self, gesture_id):
        reply = {
            "context": "robot",
            "body": {"function": "receive_mood", "message": gesture_id},
        }
        #request_message = f"robot;receive_mood;{gesture_id}"
        self.__send_message(reply)

    def send_offer(self, bid):
        reply = {
            "context": "robot",
            "body": {"function": "receive_bid", "message": str(bid)},
        }
        #request_message = f"robot;receive_bid;{str(bid)}"
        return self.__send_message(reply)

    def send_start_negotiation(self):
        reply = {
            "context": "robot",
            "body": {"function": "receive_start_nego", "message": ""},
        }
        #request_message = f"robot;receive_start_nego"
        self.__send_message(reply)

    # nego_over(type) type: "human" | "agent" | "timeline"
    def send_nego_over(self, type):
        reply = {
            "context": "robot",
            "body": {"function": "receive_nego_over", "message": type},
        }
        #request_message = f"robot;receive_nego_over;{type}"
        self.__send_message(reply)
        self.send_stop_server()

    def __send_message(self, request_message):
        context_message = request_message["context"]
        request_message.pop("context")
        reply_message = RobotMessage("CORE", request_message, context_message)
        self.queue_manager.send_message(reply_message)
        reply = self.queue_manager.wait_for_message_from_queue(HANTQueue.ROBOT)
        print("CORE",reply)
        return reply
