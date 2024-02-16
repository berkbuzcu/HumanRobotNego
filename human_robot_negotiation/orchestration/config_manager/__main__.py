import json
import pathlib

import pika

from utils import get_utility_space_json, get_preferences, get_domain_info, create_preference_xml

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import ConfigMessage
from human_robot_negotiation import DOMAINS_DIR

queue_handler = MultiQueueHandler([HANTQueue.CONFIG], host="localhost")

participant_name = "Berk Buzcu"
session_type = "Session 1"
agent_type = "Solver"
deadline = 600
facial_expression_model = "Face Channel"

domain_file = "C:/Users/Lenovo/Documents/PythonProjects/HumanRobotNego/domains/Holiday_A/Holiday_A.xml"

domain_info = get_domain_info(domain_file)

human_preferences, agent_preferences = get_preferences(domain_info["issue_names"], domain_info["issue_values_list"])

human_file_path: pathlib.Path = create_preference_xml(domain_info, participant_name, "Human", human_preferences)
agent_file_path: pathlib.Path = create_preference_xml(domain_info, participant_name, "Agent", agent_preferences)

config_message = {
    "participant_name": participant_name,
    "session_type": session_type,
    "facial_expression_model": facial_expression_model,
    "input_type": "",
    "output_type": "",
    "agent_type": agent_type,
    "agent_preferences": get_utility_space_json(str(agent_file_path.absolute())),
    "human_preferences": get_utility_space_json(str(human_file_path.absolute())),
    "robot_name": "Nao",
    "domain_info": domain_info,
    "deadline": 600,
    "camera_id": "1",
}

queue_handler.send_message(ConfigMessage("CONFIG", config_message, True))
