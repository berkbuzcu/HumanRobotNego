from abc import ABC, abstractmethod
import typing as t

from corelib.nego_action import Offer, AbstractActionFactory, NormalActionFactory, ResourceAllocationActionFactory
from corelib.utility_space import UtilitySpace


class AbstractAgent(ABC):
    sensitivity_class_list: t.List[str]
    utility_space: UtilitySpace
    action_factory: AbstractActionFactory
    name: str

    @property
    @abstractmethod
    def name(self):
        ...

    def _init_negotiation(self, preference_profile: t.Dict, domain_info: t.Dict) -> t.Tuple[bool, str]:
        self.utility_space: UtilitySpace = UtilitySpace(preference_profile)
        self.action_factory = NormalActionFactory(self.utility_space, "Agent") \
            if domain_info["domain_type"] == "normal" \
            else ResourceAllocationActionFactory(self.utility_space, "Agent")

        self.init_negotiation(preference_profile, domain_info)
        return True, f"{self.name} init complete."

    def _receive_offer(self,
                       human_offer: t.Union[Offer, None],
                       predictions: t.Dict[str, float],
                       normalized_predictions: t.Dict[str, float]
                       ):
        return self.receive_offer(human_offer, predictions, normalized_predictions)

    def _negotiation_over(self, participant_name: str, session_number: str, termination_type: str):
        return self.negotiation_over(participant_name, session_number, termination_type)

    @abstractmethod
    def init_negotiation(self, utility_space: dict, domain_info: dict):
        ...

    @abstractmethod
    def receive_offer(self, human_offer: t.Union[Offer, None], predictions: t.Dict[str, float],
                      normalized_predictions: t.Dict[str, float]) -> t.Tuple[Offer, str]:
        ...

    @abstractmethod
    def negotiation_over(self, participant_name: str, session_number: str, termination_type: str) -> None:
        ...

    @name.setter
    def name(self, value):
        self._name = value
