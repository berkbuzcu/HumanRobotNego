from abc import ABC, abstractmethod
import typing as t
from human_robot_negotiation.HANT.nego_action import Offer

class AbstractAgent(ABC):
    sensitivity_class_list: t.List[str]

    @abstractmethod
    def receive_offer(self, human_offer: t.Union[Offer, None], predictions: t.Dict[str, float], normalized_predictions: t.Dict[str, float]) -> t.Tuple[Offer, str]:
        ...

    @abstractmethod
    def receive_negotiation_over(self, participant_name: str, session_number: str, type: str) -> None:
        ...
    