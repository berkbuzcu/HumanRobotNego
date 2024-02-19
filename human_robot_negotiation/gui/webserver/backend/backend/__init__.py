import json
import random
import requests

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from .utils import *

from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.message import ConfigMessage, GUIMessage
from queuelib.enums import HANTQueue

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r"/*": {"origins": "*"}})

SERVER = "http://localhost:4000/"


@app.route("/init", methods=["GET", "POST"])
def initiate():
    queue_handler = MultiQueueHandler([HANTQueue.CONFIG])

    #participant_name = "Berk Buzcu"
    #session_type = "Session 1"
    #agent_type = "Solver"
    #deadline = 600
    #facial_expression_model = "Face Channel"
    #domain_file = "C:/Users/Lenovo/Documents/PythonProjects/HumanRobotNego/domains/Holiday_A/Holiday_A.xml"

    resp = request.get_json()
    participant_name = resp["participant_name"]
    session_type = resp["session_type"]
    agent_type = resp["agent_type"]
    facial_expression_model = resp["facial_expression_model"]

    domain_info = get_domain_info(resp["domain_file"])

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

    #preferences = {
    #    "issues": sorted(response["preferences"]["issues"].keys(),
    #                     key=response["preferences"]["issues"].get,
    #                     reverse=True),
    #}
    #
    #preferences["issue_values"] = {
    #    issue_name: sorted(response["preferences"]["issue_values"][issue_name].keys(),
    #                       key=response["preferences"]["issue_values"][issue_name].get,
    #                       reverse=True)
    #    for issue_name in preferences["issues"]
    #}

    return jsonify({"error": False}) #, "deadline": response["deadline"], "preferences": preferences})


@app.route("/preferences_info", methods=["GET", "POST"])
def get_preferences_info():
    queue_handler = MultiQueueHandler([HANTQueue.GUI])
    uuid = queue_handler.correlation_id

    queue_handler.send_message(prep_init_message(name="gui", module_type=HANTQueue.GUI))

    info = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)

    response = {"uuid": uuid, "domain_info": info}

    #response = requests.get(SERVER + "preferences_info").json() ### GET_DOMAIN_INFO HERE

    random.shuffle(response["preferences"]["issues"])

    for issue_name in response["preferences"]["issues"]:
        random.shuffle(response["preferences"]["issue_values"][issue_name])

    return jsonify(response)


@app.route("/create", methods=["GET", "POST"])
def create():
    if "preferences" not in request.json:
        return jsonify({"error": True, "errorMessage": "Preferences is required."})

    # response = requests.post(SERVER + "initiate/" + name, json={"preferences": request.json["preferences"]}).json()

    return jsonify({"error": False})


@app.route("/receive/", methods=["GET", "POST"])
def receive():
    queue_handler = MultiQueueHandler()
    message = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)

    return jsonify(json.dumps(message.payload))
