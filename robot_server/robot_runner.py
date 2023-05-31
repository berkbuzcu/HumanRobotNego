from robot_server.robot_interface import IRobot
import ast

class TestRobot(IRobot):
    def init_robot(self):
        return "test robot inited"

    def receive_start_nego(self):
        return ("nego has started")

    def receive_bid(self, offer):
        offer = ast.literal_eval(offer)

        activity_to_text = {
            "shopping": "shopping",
            "show": "see shows",
            "museum": "visiting museums",
            "sports": "do sports",
        }

        return ("I'd like to visit %s in %s for %s and stay at a %s" % (offer['destination'], offer['season'], activity_to_text[offer['events']], offer['accommodation']))
    
    def receive_mood(self, mood):
        return ("wooohooo! " + mood)

    def receive_nego_over(self, type):
        return ("nego over type: " + type)
    

class RobotServer:
    def __init__(self, channel):
        self.server_stopped = False
        self.channel = channel
        self.robot = None

    def start_server(self):
        while not self.server_stopped:
            message = self.channel.receive()
            parsed_message = list(filter(None, message.split(";")))

            #EX: message: server;stop_server|init_robot || robot;receive_mood;dissatisfied_1 
            func_selector = {
                "server": self,
                "robot":  self.robot,
            }

            try:
                func = getattr(func_selector[parsed_message[0]], parsed_message[1])
                reply = func(*parsed_message[2:])
                self.channel.send("Execution successful. INPUT: %s: REPLY: %s" % (str(parsed_message), str(reply)))

            except Exception as e:
                self.channel.send("Failed: %s" % e)
    
    def init_robot(self, robot_name):
        robot_class = TestRobot
        if robot_name == "nao":
            from robot_server.nao.robot_mobile_action import RobotMobileAction
            robot_class = RobotMobileAction

        elif robot_name == "pepper":
            from robot_server.pepper.robot_mobile_action import RobotMobileAction
            robot_class = RobotMobileAction
        
        elif robot_name == "qt":
            from robot_server.qt.QTtest import QTRobotClass
            robot_class = QTRobotClass
        else:
            self.channel.send("Failed: %s" % robot_name)

        self.robot = robot_class()
        return self.robot.init_robot()

    def stop_server(self):
        self.server_stopped = True

if __name__ == "__channelexec__":
    RobotServer(channel).start_server()
    