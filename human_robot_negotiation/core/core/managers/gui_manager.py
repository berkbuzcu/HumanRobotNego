import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import GUIMessage
from .abstract_manager import AbstractManager


class GUIManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def __init__(self):
        super().__init__()
        self.message_payload = {
            "message": "",
            "offer_content": {},
            "round": 0,
            "status": "AGENT_LISTENING",
            "utility": 0,
            "is_completed": False,
            "who": "HUMAN",
        }

    def update_status(self, text):
        if text == "AGENT_LISTENING":
            self.message_payload["round"] += 1
        self.message_payload["status"] = text

    def reset_offer_grid(self):
        self.message_payload["offer_content"] = {}

    def update_offer_grid(self, bidder, offer):
        self.message_payload["offer_content"] = offer
        self.message_payload["who"] = bidder

    def update_offer_message(self, bidder, text):
        self.message_payload["who"] = bidder
        self.message_payload["message"] = text

    def update_offer_utility(self, bidder, text):
        self.message_payload["who"] = bidder
        self.message_payload["utility"] = int(text)

    def send_gui_message(self):
        gui_message = GUIMessage("CORE", self.message_payload, "custom")
        self.queue_manager.send_message(gui_message)
