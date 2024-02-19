import pika
import time
from .qt_robot import QTRobotClass
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue
from queuelib.message import RobotMessage
class RobotServer:
    def __init__(self):
        self.queue_manager = MultiQueueHandler()

        self.server_stopped = False
        self.robot = None
        self.queue_manager.send_message(prep_init_message("Qt",HANTQueue.ROBOT))

    def start_server(self):
        while not self.server_stopped:
            message = self.queue_manager.wait_for_message_from_queue(HANTQueue.ROBOT)
            print("MESSAGE TYPE: ",type(message))
            print("MESSAGE : ",message)
            #message=message.decode('utf-8')
            message_from = message.sender
            message_payload = message.payload # {body:{function:"recive_mood",message:"Dissatisfied"}}
            payload_context = message.context # robot|server

            func_selector = {
                "server": self,
                "robot": self.robot,
            }



            try:
                func = getattr(func_selector[payload_context], message_payload['body']['function'])
                reply = {
                    "context": payload_context,
                    "body": {},
                    "status": "true",
                }
                if(message_payload['body']['message']==""):
                    reply["body"]  = func()
                else:
                    reply["body"]  = func(message_payload['body']['message'])

                reply_message= RobotMessage("qt", reply)
                self.queue_manager.send_message(reply_message)

            except Exception as e:
                reply = {
                    "context": payload_context,
                    "body": {"error" : str(e)},
                    "status": "false",
                }
                reply_message = RobotMessage("qt",reply)
                self.queue_manager.send_message(reply_message)


    def init_robot(self):
        self.robot = QTRobotClass()
        return self.robot.init_robot()

    def stop_server(self):
        self.server_stopped = True
        return self.robot.stop_robot()


server = RobotServer()
server.init_robot()
server.start_server()
