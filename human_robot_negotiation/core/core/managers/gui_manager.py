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
            "message": None,
            "offer_content": None,
            "round": None,
            "status": None,
            "utility": None,
            "is_completed": None,
            "who": None,
        }

    def update_status(self, text):
        self.message_payload["status"] = text
        gui_message = GUIMessage("CORE", self.message_payload, "status")
        self.queue_manager.send_message(gui_message)

    def reset_offer_grid(self):
        self.message_payload["offer_content"] = None
        gui_message = GUIMessage("CORE", self.message_payload, "reset_offer_grid")
        self.queue_manager.send_message(gui_message)

    def update_offer_grid(self, bidder, offer):
        self.message_payload["offer_content"] = offer.to_json_str()
        self.message_payload["who"] = bidder
        gui_message = GUIMessage("CORE", self.message_payload, "offer_grid")
        self.queue_manager.send_message(gui_message)

    def update_offer_message(self, bidder, text):
        self.message_payload["who"] = bidder
        self.message_payload["message"] = text

        gui_message = GUIMessage("CORE", self.message_payload, "offer_grid")
        self.queue_manager.send_message(gui_message)

    def update_offer_utility(self, bidder, text):
        self.message_payload["who"] = bidder
        self.message_payload["utility"] = text
        gui_message = GUIMessage("CORE", self.message_payload, "offer_grid")
        self.queue_manager.send_message(gui_message)
