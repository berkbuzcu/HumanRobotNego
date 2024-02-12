import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from .abstract_manager import AbstractManager


class RobotManager:
    queue_handler: MultiQueueHandler

    ### Server Methods ###
    def send_init_robot(self, robot_name):
        request_message = f"server;init_robot;{robot_name.lower()}"
        self.__send_message(request_message)

    def send_stop_server(self):
        request_message = "server;stop_server"
        self.__send_message(request_message)

    ### Robot Methods ###
    def send_mood(self, gesture_id):
        request_message = f"robot;receive_mood;{gesture_id}"
        self.__send_message(request_message)

    def send_offer(self, bid):
        request_message = f"robot;receive_bid;{str(bid)}"
        return self.__send_message(request_message)

    def send_start_negotiation(self):
        request_message = f"robot;receive_start_nego"
        self.__send_message(request_message)

    # nego_over(type) type: "human" | "agent" | "timeline"
    def send_nego_over(self, type):
        request_message = f"robot;receive_nego_over;{type}"
        self.__send_message(request_message)
        self.send_stop_server()

    def __send_message(self, request_message):
        self.queue_handler.send_message(HANTQueue.ROBOT, json.dumps(request_message))
        reply = self.queue_handler.wait_for_message_from_queue(HANTQueue.ROBOT)
        return reply[reply.find("REPLY:") + len("REPLY:"):]
