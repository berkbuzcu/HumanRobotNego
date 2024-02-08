import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from corelib.nego_action import Offer


class HumanInteractionManager:
    def __init__(self):
        self.queue_manager = MultiQueueHandler()

    # (human_action, offer_done, total_user_input) = self.human_interaction_controller.get_human_action()
    def get_human_action(self):
        msg_dict = json.loads(self.queue_manager.wait_for_message_from_queue(HANTQueue.HUMAN.value))
        return Offer.from_json(msg_dict["offer"]), msg_dict["offer_done"], msg_dict["total_user_input"]
