import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue

class GUIManager:
    def __init__(self):
        self.queue_manager = MultiQueueHandler()

    def update_status(self, text):
        message = {
            "type": "status",
            "body": text,
            "bidder": None
        }

        self.queue_manager.send_message(HANTQueue.GUI, json.dumps(message))

    def reset_offer_grid(self):
        message = {
            "type": "board",
            "bidder": None,
            "body": None,
        }

        self.queue_manager.send_message(HANTQueue.GUI, json.dumps(message))

    def update_offer_grid(self, bidder, offer):
        message = {
            "type": "message",
            "bidder": bidder,
            "body": offer.to_json_str(),
        }

        self.queue_manager.send_message(HANTQueue.GUI, json.dumps(message))

    def update_offer_message(self, bidder, text):
        message = {
            "type": "message",
            "body": text,
            "bidder": bidder
        }

        self.queue_manager.send_message(HANTQueue.GUI, json.dumps(message))

    def update_offer_utility(self, bidder, text):
        message = {
            "type": "message",
            "body": text,
            "bidder": bidder
        }

        self.queue_manager.send_message(HANTQueue.GUI, json.dumps(message))

