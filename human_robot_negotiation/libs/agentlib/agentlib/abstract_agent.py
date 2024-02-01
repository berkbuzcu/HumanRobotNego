from abc import ABC, abstractmethod
import typing as t

from corelib.nego_action import Offer
from queuelib.queue_manager import MultiQueueHandler


class AbstractAgent(ABC):
    sensitivity_class_list: t.List[str]

    def __init__(self):
        self.hant_queue = MultiQueueHandler(["agent", "logger"])

    def _receive_offer(self,
                       human_offer: t.Union[Offer, None],
                       predictions: t.Dict[str, float],
                       normalized_predictions: t.Dict[str, float]
                       ):
        message = self.hant_queue.wait_for_message_from_queue("agent")

        self.receive_offer(human_offer, predictions, normalized_predictions)

    @abstractmethod
    def receive_offer(self, human_offer: t.Union[Offer, None], predictions: t.Dict[str, float],
                      normalized_predictions: t.Dict[str, float]) -> t.Tuple[Offer, str]:
        ...

    @abstractmethod
    def receive_negotiation_over(self, participant_name: str, session_number: str, type: str) -> None:
        ...
