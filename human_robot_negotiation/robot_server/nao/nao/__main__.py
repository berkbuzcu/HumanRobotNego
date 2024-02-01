import pika
from nao_robot import NaoRobot
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue


class RobotServer:
    def __init__(self):
        self.queue_manager = MultiQueueHandler(HANTQueue.ROBOT)

        self.server_stopped = False
        self.robot = None

    def start_server(self):
        while not self.server_stopped:
            message = self.queue_manager.wait_for_message_from_queue(HANTQueue.ROBOT)

            parsed_message = list(filter(None, message.split(";")))

            # EX: message: server;stop_server|init_robot || robot;receive_mood;dissatisfied_1
            func_selector = {
                "server": self,
                "robot": self.robot,
            }

            try:
                func = getattr(func_selector[parsed_message[0]], parsed_message[1])
                reply = func(*parsed_message[2:])
                self.queue_manager.send_message(HANTQueue.ROBOT,
                                                "Execution successful. INPUT: %s: REPLY: %s" %
                                                (str(parsed_message), str(reply)))

            except Exception as e:
                self.queue_manager.send_message("Failed: %s" % e)

    def init_robot(self):
        self.robot = NaoRobot()
        return self.robot.init_robot()

    def stop_server(self):
        self.server_stopped = True


server = RobotServer()
server.init_robot()
server.start_server()
