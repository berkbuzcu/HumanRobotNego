import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import HumanMessage
from corelib.nego_action import Offer
from .abstract_manager import AbstractManager


class HumanInteractionManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def get_human_action(self):
        human_message = HumanMessage("CORE", {"action": "get_human_offer"}, True)
        self.queue_manager.send_message(human_message)
        msg_dict = self.queue_manager.wait_for_message_from_queue(HANTQueue.HUMAN).payload
        return Offer.from_json(msg_dict["offer"]), msg_dict["offer_done"], msg_dict["total_user_input"]
