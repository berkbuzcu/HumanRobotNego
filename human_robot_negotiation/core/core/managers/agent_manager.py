import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import AgentMessage
from corelib.nego_action import Offer
from .abstract_manager import AbstractManager


class AgentManager(AbstractManager):
    queue_manager: MultiQueueHandler

    def send_offer(self, offer: Offer, predictions, normalized_predictions, current_time) -> None:
        message = {
            "predictions": predictions,
            "normalized_predictions": normalized_predictions,
            "offer": offer.to_json_str(),
            "current_time": current_time,
        }

        self.queue_manager.send_message(AgentMessage("CORE", message, "receive_bid"))

    def receive_offer(self):
        message = self.queue_manager.wait_for_message_from_queue(HANTQueue.AGENT)
        agent_offer = Offer.from_json(message.payload["offer"])
        agent_mood = message.payload.get("mood", None)
        return agent_offer, agent_mood

    def send_negotiation_over(self, participant_name, session_number, termination_type: str) -> None:
        self.queue_manager.send_message(
            AgentMessage("CORE",
                         {"termination_type": termination_type,
                          "session_number": session_number,
                          "participant_name": participant_name},
                         "termination"))
