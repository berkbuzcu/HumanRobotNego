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
    queue_handler = MultiQueueHandler([HANTQueue.CONFIG])

    resp = {to_snake_case(key): value for key, value in dict(request.get_json()).items()}
    print("resp ", resp)

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

    queue_handler.correlation_id = resp["user_name"]
    queue_handler.send_message(ConfigMessage("CONFIG", config_message, context="config"))
    return jsonify({"uuid": resp["user_name"], "error": False})


@app.route("/preferences_info", methods=["GET", "POST"])
def get_preferences_info():
    uuid = dict(request.json)["uuid"]
    queue_handler = MultiQueueHandler([HANTQueue.GUI], uuid)

    domain_info = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)

    random.shuffle(domain_info.payload["issue_names"])

    for issue_name in domain_info.payload["issue_values_list"].keys():
        random.shuffle(domain_info.payload["issue_values_list"][issue_name])

    print("Responses from pref info ", domain_info.payload)
    return jsonify(domain_info.payload)


@app.route("/create_preferences", methods=["GET", "POST"])
def create_preferences():
    uuid = request.json["uuid"]
    queue_handler = MultiQueueHandler([HANTQueue.CONFIG], correlation_id=uuid)
    ordered_preferences = request.json["preferences"]
    domain_info = request.json["domain_info"]

    human_preferences, agent_preferences = get_preferences(ordered_preferences["issues"],
                                                           ordered_preferences["issue_values"])

    queue_handler.send_message(ConfigMessage("CONFIG",
                                             {"human_preferences": agent_preferences,
                                              "agent_preferences": human_preferences},
                                             "preferences"))

    create_preference_xml(domain_info, uuid, "Human", human_preferences)
    create_preference_xml(domain_info, uuid, "Agent", agent_preferences)

    return jsonify({"status": "success"})


@app.route("/start_negotiation/", methods=["GET", "POST"])
def start_negotiation():
    uuid = request.json["uuid"]
    queue_handler = MultiQueueHandler([HANTQueue.GUI], correlation_id=uuid)
    init_message = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)

    return jsonify({"error": False, **init_message.payload})


@app.route("/receive/", methods=["GET", "POST"])
def receive():
    queue_handler = MultiQueueHandler(HANTQueue.GUI)
    queue_handler.send_message(prep_init_message(name="gui", module_type=HANTQueue.GUI))

    message = queue_handler.wait_for_message_from_queue(HANTQueue.GUI)

    return jsonify(json.dumps(message.payload))
