
from email import message
from pydoc import cli
from urllib import request

class RobotClient:
    def __init__(self, channel) -> None:
        self.channel = channel

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
    
    def send_bid(self, bid):
        request_message = f"robot;receive_bid;{str(bid)}"
        return self.__send_message(request_message)

    def send_start_negotiation(self):
        request_message = f"robot;receive_start_nego"
        self.__send_message(request_message)

    #nego_over(type) type: "human" | "agent" | "timeline"
    def send_nego_over(self, type):
        request_message = f"robot;receive_nego_over;{type}"
        self.__send_message(request_message)

        self.send_stop_server()

    def __send_message(self, request_message):
        self.channel.send(request_message)
        reply = self.channel.receive()
        print("Received reply %s [ %s ]" % (request_message, reply))
        return reply[reply.find("REPLY:")+len("REPLY:"):]

#gw = execnet.makegateway("popen//python=D:\PythonProjects\Human-Robot-Nego\AgentInteractionModels\.venv\Scripts\python.exe")
#channel = gw.remote_exec("""
#    from AgentInteractionModels.robot_server import RobotServer
#    robot_server = RobotServer(channel)
#    robot_server.start_server()
#    """)
#
#client = RobotClient(channel)
#client.send_init_robot("test")
#client.send_stop_server()