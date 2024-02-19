import time

from queuelib.message import *
from queuelib.queue_manager import MultiQueueHandler
from .core import Core

queue_list = set([e for e in HANTQueue])
validation_modules = [HANTQueue.GUI, HANTQueue.AGENT, HANTQueue.EMOTION, HANTQueue.ROBOT,
                      HANTQueue.LOGGER, HANTQueue.HUMAN, HANTQueue.MICROPHONE, HANTQueue.CAMERA]
validation_done = set()

queue_handler = MultiQueueHandler(queue_list, correlation_id="CORE")

### First get the config from the config manager ###
core_config = queue_handler.wait_for_message_from_queue(HANTQueue.CONFIG)
print("Received core config: ", core_config)

hant_core = Core(core_config.payload)

domain_info_message = GUIMessage("CORE", hant_core.domain_info, "domain_info")
print("Sending domain info message: ")
queue_handler.send_message(domain_info_message)

### Get the utility spaces from the GUI ###
utility_spaces = queue_handler.wait_for_message_from_queue(HANTQueue.CONFIG)

print("Received utility spaces: ", utility_spaces)
hant_core.set_utility_spaces(utility_spaces.payload)

## Send the nego start message to the GUI
gui_messsage = GUIMessage("CORE", {"deadline": hant_core.deadline,
                                   "preferences": hant_core.human_preferences.get_ordered_issues()}, "gui_grid")
queue_handler.send_message(gui_messsage)

## VALIDATION IS IGNORED FOR NOW
"""
def is_validation_done():
    return len(validation_done) == len(validation_modules)


def validate_sub_modules(ch, method, properties, body: AbstractMessage):
    queue_name = method.routing_key

    if body.sender == "CORE":
        return

    validation_done.add(queue_name)

    print("MODULE REGISTERED TO CORE: ", body.sender, body.status)

    if body.status:
        validation_done.add(queue_name)

    else:
        print(body.payload["error"])

    if len(validation_done) == len(queue_list):
        ch.stop_consuming()


print("--- WAITING OTHER COMPONENTS ---")
queue_handler.consume_all_queues_with_callback(validate_sub_modules)

while not is_validation_done():
    print("CORE: --- WAITING SUB-SYSTEMS ---")
    print(queue_list - validation_done)
    time.sleep(2)
"""


queue_handler.flush_queues()

### INIT MODULES ###
init_agent_message = AgentMessage("CORE", {"utility_space": hant_core.agent_utility_space.to_dict(),
                                           "domain_info": hant_core.domain_info}, context="init_negotiation")

init_emotion_message = EmotionMessage("CORE", {"participant_name": hant_core.participant_name,
                                               "session_number": hant_core.session_number,
                                               "session_type": hant_core.session_type}, context="init")
init_human_interaction_message = HumanMessage("CORE", {"domain_info": hant_core.domain_info}, context="init")

init_camera_message = CameraMessage("CORE", {"username": hant_core.participant_name}, context="init")

hant_core.robot_manager.send_start_negotiation()

queue_handler.send_message(init_agent_message)
queue_handler.send_message(init_emotion_message)
queue_handler.send_message(init_human_interaction_message)

print("--- SUB-SYSTEMS COMPLETE ---")
print("STARTING NEGOTIATION...")

hant_core.negotiate()
