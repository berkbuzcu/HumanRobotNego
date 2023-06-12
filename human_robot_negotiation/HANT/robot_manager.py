import execnet
import os 
import sys

from human_robot_negotiation import ROBOT_SERVER_DIR, REQUIREMENTS_DIR
from robot_server import robot_runner

class RobotManager:
    channel: execnet.gateway_base.Channel
    ### Server Methods ###

    def send_init_robot(self, robot_name):
        request_message = f"server;init_robot;{robot_name.lower()}"
        print("MSG: ", request_message)
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
    
    def venv_manager(self, agent_interaction_type):
        python2_path="C:\\Python27\\python.exe"
        
        python3_path=sys.executable

        venv_path=str(ROBOT_SERVER_DIR / f".venv_{agent_interaction_type}")
        python2_command=" -m virtualenv " + venv_path
        python3_command=" -m venv "+ venv_path
        
        if not os.path.isdir(venv_path):
            REQUIREMENTS_FILE = REQUIREMENTS_DIR / f"requirements{agent_interaction_type}.txt"
            if agent_interaction_type=="Nao" or agent_interaction_type=="Pepper":
                os.system(python2_path+python2_command)
            elif agent_interaction_type=="QT":
                os.system(python3_path+python3_command)   #for any new robot add a elif agent_interaction_type=="RobotName" with suitable python version.

            command = (ROBOT_SERVER_DIR / f".venv_{agent_interaction_type}" / agent_interaction_type / "Scripts" / "activate").absolute
            os.system(f"{command} && pip install -r {REQUIREMENTS_FILE.absolute}")

    def start_robot_server(self, agent_interaction_type):
        self.venv_manager(agent_interaction_type)
        if agent_interaction_type=="Nao" or agent_interaction_type=="Pepper":
            agent_interaction_type="Nao"
        python_exe = str(ROBOT_SERVER_DIR / f".venv_{agent_interaction_type}" / "Scripts" / "python.exe")
        venvPath=f"popen//python={python_exe}"
        gw = execnet.makegateway(venvPath)
        self.channel = gw.remote_exec(robot_runner)
        self.send_init_robot(agent_interaction_type)