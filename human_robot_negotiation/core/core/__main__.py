import time

from queuelib.message import *
from queuelib.queue_manager import MultiQueueHandler
from .core import Core

queue_list = set([e for e in HANTQueue])
validation_done = set()

queue_handler = MultiQueueHandler(queue_list, correlation_id="CORE")

### First get the config from the config manager ###
core_config = queue_handler.wait_for_message_from_queue(HANTQueue.CONFIG)

hant_core = Core(core_config.payload)

### Get the utility spaces from the GUI ###
domain_info_message = GUIMessage("CORE", hant_core.domain_info, "domain_info")
queue_handler.send_message(domain_info_message)

utility_spaces = queue_handler.wait_for_message_from_queue(HANTQueue.CONFIG)

hant_core.set_utility_spaces(utility_spaces.payload)


def is_validation_done():
    return validation_done == len(queue_list)


def validate_sub_modules(ch, method, properties, body: AbstractMessage):
    queue_name = method.routing_key

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

print("--- SUB-SYSTEMS COMPLETE ---")
print("--- WAITING FOR CONFIG ---")

### INIT MODULES ###
init_agent_message = AgentMessage("CORE", hant_core.agent_utility_space, True)
queue_handler.send_message(init_agent_message)

init_gui_message = GUIMessage("CORE", hant_core.domain_info, True)
queue_handler.send_message(init_gui_message)

hant_core.negotiate()
