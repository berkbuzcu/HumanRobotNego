import pika
import threading
import traceback
import json
import xml

from human_robot_negotiation import DOMAINS_DIR
from utils import get_utility_space_json, get_preferences, get_domain_info, create_preference_xml

host = 'localhost'
queues = ["internal", "robot_server", "gui", "emotion", "logger"]
credentials = pika.PlainCredentials("orchestrator", "orchestrator")

connection = pika.BlockingConnection(host, 5672)
channel = connection.channel()

participant_name = "Berk Buzcu"
session_type = "Session 1"
agent_type = "Solver"
deadline = 600
facial_expression_model = "Face Channel"

domain_file = "C:/Users/Lenovo/Documents/PythonProjects/HumanRobotNego/domains/Holiday_A/Holiday_A.xml"

domain_info = get_domain_info(domain_file)

human_preferences, agent_preferences = get_preferences(domain_info["issue_names"], domain_info["issue_values_list"])

create_preference_xml(domain_info, participant_name, "Human", human_preferences)
create_preference_xml(domain_info, participant_name, "Agent", agent_preferences)


config_message = {
    "participant_name": participant_name,
    "session_type": session_type,
    "facial_expression_model": facial_expression_model,
    "input_type": "",
    "output_type": "",
    "agent_type": agent_type,
    "agent_preferences": get_utility_space_json(human_preferences),
    "human_preferences": get_utility_space_json(agent_preferences),
    "robot_name": "Nao",
    "domain_info": domain_info,
    "deadline": 600,
    "camera_id": "1",
}

channel.basic_publish(
    exchange='',
    routing_key="internal",
    body=json.dumps(config_message),
    properties=pika.BasicProperties(
        delivery_mode=2,
    )
)

print(f"Message sent to queue internal: {json.dumps(config_message)}")
