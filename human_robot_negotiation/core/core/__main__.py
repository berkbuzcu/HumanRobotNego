import time
import xml


from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from .core import Core

queue_handler = MultiQueueHandler([e for e in HANTQueue])
validation_done = []


def validate_sub_modules(ch, method, properties, body):
    queue_name = method.routing_key
    validation_done.append(queue_name)

    if len(validation_done) == len([e for e in HANTQueue]):
        ch.stop_consuming()


queue_handler.consume_all_queues_with_callback(validate_sub_modules)

while not validation_done:
    print("--- WAITING SUB-SYSTEMS ---")
    time.sleep(2)

print("--- SUB-SYSTEMS COMPLETE ---")
print("--- WAITING FOR CONFIG ---")

### First get the config from the config manager ###
core_config = queue_handler.wait_for_message_from_queue("internal")

hant_core = Core(queue_handler, core_config)

### INIT MODULES ###
queue_handler.send_message("agent", hant_core.agent_utility_space)
