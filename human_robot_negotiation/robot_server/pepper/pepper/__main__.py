import ast
import pika


class RobotServer:
    def __init__(self):
        self.server_stopped = False
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()
        self.robot = None

    def start_server(self):
        while not self.server_stopped:
            message = self.channel.basic_ack()
            parsed_message = list(filter(None, message.split(";")))

            # EX: message: server;stop_server|init_robot || robot;receive_mood;dissatisfied_1
            func_selector = {
                "server": self,
                "robot": self.robot,
            }

            try:
                func = getattr(func_selector[parsed_message[0]], parsed_message[1])
                reply = func(*parsed_message[2:])
                self.channel.send("Execution successful. INPUT: %s: REPLY: %s" % (str(parsed_message), str(reply)))

            except Exception as e:
                self.channel.send("Failed: %s" % e)

    def init_robot(self):
        from pepper_robot import PepperRobot
        self.robot = PepperRobot()
        return self.robot.init_robot()

    def stop_server(self):
        self.server_stopped = True

server = RobotServer()
server.init_robot()
server.start_server()
