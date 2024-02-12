import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from .abstract_manager import AbstractManager


class GUIManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def __init__(self):
        super().__init__()
        self.message = {
            "message": None,
            "offer_content": None,
            "round": None,
            "status": None,
            "utility": None,
            "is_completed": None,
            "who": None,
        }

    def update_status(self, text):
        self.message["status"] = text

        self.queue_manager.send_message(HANTQueue.GUI.value, json.dumps(self.message))

    def reset_offer_grid(self):
        message = {
            "type": "board",
            "bidder": None,
            "body": None,
        }

        self.queue_manager.send_message(HANTQueue.GUI.value, json.dumps(message))

    def update_offer_grid(self, bidder, offer):
        # message = {
        #    "type": "message",
        #    "bidder": bidder,
        #    "body": offer.to_json_str(),
        # }

        self.message["offer_content"] = offer.to_json_str()

        self.queue_manager.send_message(HANTQueue.GUI.value, json.dumps(self.message))

    def update_offer_message(self, bidder, text):
        # message = {
        #    "type": "message",
        #    "body": text,
        #    "bidder": bidder
        # }

        self.message["who"] = bidder
        self.message["message"] = text

        self.queue_manager.send_message(HANTQueue.GUI.value, json.dumps(self.message))

    def update_offer_utility(self, bidder, text):
        # message = {
        #     "type": "message",
        #     "body": text,
        #     "bidder": bidder
        # }

        self.message["who"] = bidder
        self.message["utility"] = text
        self.queue_manager.send_message(HANTQueue.GUI.value, json.dumps(self.message))
