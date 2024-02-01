import json

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from corelib.nego_action import Offer


class AgentManager:
    queue_manager: MultiQueueHandler

    def __init__(self):
        self.queue_manager = MultiQueueHandler()

    def send_offer(self, offer: Offer, predictions, normalized_predictions) -> None:
        message = {
            "type": "offer",
            "predictions": predictions,
            "normalized_predictions": normalized_predictions,
            "offer": offer.to_json_str(),
        }

        self.queue_manager.send_message(HANTQueue.AGENT, json.dumps(message))

    def receive_offer(self):
        msg = self.queue_manager.wait_for_message_from_queue(HANTQueue.AGENT)
        agent_offer = Offer.from_json(msg["offer"])
        agent_mood = msg["mood"]
        return agent_offer, agent_mood
