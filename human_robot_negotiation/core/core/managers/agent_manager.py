import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import AgentMessage
from corelib.nego_action import Offer
from .abstract_manager import AbstractManager


class AgentManager(AbstractManager):
    queue_manager: MultiQueueHandler

    def send_offer(self, offer: Offer, predictions, normalized_predictions) -> None:
        message = {
            "context": "offer",
            "predictions": predictions,
            "normalized_predictions": normalized_predictions,
            "offer": offer.to_json_str(),
        }

        self.queue_manager.send_message(AgentMessage("CORE", message, True))

    def receive_offer(self):
        message = self.queue_manager.wait_for_message_from_queue(HANTQueue.AGENT)
        agent_offer = Offer.from_json(message.payload["offer"])
        agent_mood = message.payload["mood"]
        return agent_offer, agent_mood
