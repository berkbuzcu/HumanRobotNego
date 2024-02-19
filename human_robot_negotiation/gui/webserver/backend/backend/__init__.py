import json
import random
import re
from flask import Flask, jsonify, request
from flask_cors import CORS

from queuelib.enums import HANTQueue
from queuelib.message import ConfigMessage
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from .utils import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()

@app.route("/initiate/", methods=["GET", "POST"])
def initiate():
    # participant_name = "Berk Buzcu"
    # session_type = "Session 1"
    # agent_type = "Solver"
    # deadline = 600
    # facial_expression_model = "Face Channel"
    # domain_file = "C:/Users/Lenovo/Documents/PythonProjects/HumanRobotNego/domains/Holiday_A/Holiday_A.xml"

    resp = {to_snake_case(key): value for key, value in dict(request.get_json()).items()}
    print("resp: ", resp)

    domain_info = resp["domain_file"][resp["domain_file"].find("/domains"):]
    domain_info = get_domain_info(domain_info)

    config_message = {
        "participant_name": resp["user_name"],
        "session_type": resp["session_type"],
        "facial_expression_model": resp["facial_expression_model"],
        "input_type": resp["human_input"],
        "output_type": "",
        "agent_type": resp["agent_type"],
        "robot_name": resp["robot_type"],
        "domain_info": domain_info,
        "deadline": resp["deadline"],
        "camera_id": "1",
    }

    queue_handler = MultiQueueHandler([HANTQueue.CONFIG], correlation_id=resp["user_name"])
    uuid = queue_handler.correlation_id

    queue_handler.send_message(ConfigMessage("CONFIG", config_message, context="config"))

    # preferences = {
    #    "issues": sorted(response["preferences"]["issues"].keys(),
    #                     key=response["preferences"]["issues"].get,
    #                     reverse=True),
    # }
    #
    # preferences["issue_values"] = {
    #    issue_name: sorted(response["preferences"]["issue_values"][issue_name].keys(),
    #                       key=response["preferences"]["issue_values"][issue_name].get,
    #                       reverse=True)
    #    for issue_name in preferences["issues"]
    # }

    return jsonify({"uuid: ": uuid, "error": False})  # , "deadline": response["deadline"], "preferences": preferences})


@app.route("/preferences_info", methods=["GET", "POST"])
def get_preferences_info():
    uuid = request.json["uuid"]

    queue_handler = MultiQueueHandler([HANTQueue.GUI], correlation_id=uuid)
    domain_info = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)
    response = {"uuid": uuid, "domain_info": domain_info.payload}

    random.shuffle(response["preferences"]["issues"])

    for issue_name in response["preferences"]["issues"]:
        random.shuffle(response["preferences"]["issue_values"][issue_name])

    return jsonify(response)


@app.route("/create_preferences", methods=["GET", "POST"])
def create_preferences():
    uuid = request.json["uuid"]
    queue_handler = MultiQueueHandler([HANTQueue.GUI], correlation_id=uuid)
    participant_name = request.json["ordered_preferences"]
    ordered_preferences = request.json["ordered_preferences"]
    domain_info = request.json["domain_info"]

    human_preferences, agent_preferences = get_preferences(ordered_preferences["issue_names"],
                                                           ordered_preferences["issue_values_list"])

    human_file_path: pathlib.Path = create_preference_xml(domain_info, participant_name, "Human", human_preferences)
    agent_file_path: pathlib.Path = create_preference_xml(domain_info, participant_name, "Agent", agent_preferences)
    # "agent_preferences": get_utility_space_json(str(agent_file_path.absolute())),
    # "human_preferences": get_utility_space_json(str(human_file_path.absolute())),

    return jsonify({"status": "success"})

@app.route("/create", methods=["GET", "POST"])
def create():
    if "preferences" not in request.json:
        return jsonify({"error": True, "errorMessage": "Preferences is required."})

    domain_info = request.json["domain_info"]

    # response = requests.post(SERVER + "initiate/" + name, json={"preferences": request.json["preferences"]}).json()

    return jsonify({"error": False})


@app.route("/receive/", methods=["GET", "POST"])
def receive():
    queue_handler = MultiQueueHandler(HANTQueue.GUI)
    queue_handler.send_message(prep_init_message(name="gui", module_type=HANTQueue.GUI))

    message = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)

    return jsonify(json.dumps(message.payload))
