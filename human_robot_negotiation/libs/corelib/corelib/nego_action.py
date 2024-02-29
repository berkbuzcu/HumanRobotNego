import random
import typing as t
from abc import ABC, abstractmethod
from random import randrange

from .utility_space import UtilitySpace
import json


class AbstractAction(object):
    @abstractmethod
    def get_bid(self, perspective: t.Union[str, None] = None) -> t.Dict[str, str]:
        ...

    @classmethod
    def from_json(cls, bid_json):
        offer_dict = json.loads(bid_json)
        if offer_dict.get("acceptor", None):
            return Accept(offer_dict["acceptor"])

        bidder = offer_dict["bidder"]
        bid = offer_dict["bid"]
        reverse_swap = {"Agent": "Human", "Human": "Agent"}
        return Offer(bid[bidder], bid[reverse_swap[bidder]], offer_dict["bidder"])

class Accept(AbstractAction):
    def __init__(self, acceptor="Agent"):
        super().__init__()
        self.__bid = None
        self.__acceptor = acceptor

    def set_bid(self, bid):
        self.__bid = bid

    def get_acceptor(self):
        return self.__acceptor

    def get_bid(self, perspective: t.Union[str, None] = None):
        return self.__bid

    def to_json_str(self):
        return json.dumps({
            "acceptor": self.__acceptor
        })


class Offer(AbstractAction):
    def __init__(self, bidder_perspective, reverse_perspective, bidder):
        super().__init__()
        self.__bidder = bidder

        if bidder is None: raise ValueError("Invalid bidder")

        # bidder = Agent | Human
        reverse_swap = {"Agent": "Human", "Human": "Agent"}
        self.__bid_perspectives = {bidder: bidder_perspective, reverse_swap[bidder]: reverse_perspective}

    def get_bidder(self):
        return self.__bidder

    def get_bid(self, perspective: t.Union[str, None] = None) -> t.Dict[str, str]:
        if not perspective:
            return self.__bid_perspectives[self.__bidder]

        return self.__bid_perspectives[perspective]

    def to_json_str(self):
        return json.dumps({
            "bidder": self.__bidder,
            "bid": self.__bid_perspectives
        })




    def __str__(self):
        bid_str = " ".join(map(str, self.__bid_perspectives[self.__bidder].values()))
        return bid_str

    def __getitem__(self, issue):
        return self.get_bid(self.__bidder)[issue]  # Get bid from bidder perspective

    def __hash__(self) -> int:
        return sum([hash(item) for item in self.get_bid().values()])

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Offer):
            return set(self.get_bid("Agent").values()) == set(__o.get_bid("Agent").values())
        raise TypeError(f"Comparing invalid types of bids: ({type(self)} -> {type(__o)})")


class AbstractActionFactory(ABC):
    def __init__(self, utility_space: UtilitySpace, bidder: str):
        if bidder is None: raise ValueError("Invalid bidder")

        self.utility_manager = utility_space
        self.bidder = bidder

    @abstractmethod
    def factory_method(self, offer_details: dict) -> Offer:
        pass

    def create_acceptance(self) -> Accept:
        return Accept(acceptor=self.bidder)

    def create_offer(self, offer_details: dict) -> Offer:
        return self.factory_method(offer_details)

    def get_offer_between_utility(
            self,
            lower_utility_threshold: float,
            upper_utility_threshold: float) -> Offer:
        filtered_offers = []
        while len(filtered_offers) == 0:
            filtered_offers = [x for x in self.utility_manager.all_possible_offers
                               if (
                                           lower_utility_threshold <= self.utility_manager.get_offer_utility(x) < upper_utility_threshold
                                           )]
            upper_utility_threshold += 0.01
            lower_utility_threshold -= 0.01
        random_offer_index = randrange(0, len(filtered_offers))
        random_offer = filtered_offers[random_offer_index]
        return self.create_offer(random_offer)

    def get_offer_below_utility(self, target_utility) -> Offer:
        bids_utils = list(
            zip(self.utility_manager.all_possible_offers, self.utility_manager.get_all_possible_offers_utilities()))
        bids_utils.sort(key=lambda x: x[1], reverse=True)

        idx = 0
        for idx, (bid, utility) in enumerate(bids_utils):
            if utility < target_utility:
                break

        offer = random.choice(bids_utils[idx:idx + 3])[0]
        return self.create_offer(offer)

    def get_offer_above_utility(self, lower_utility_threshold) -> Offer:
        upper_utility_threshold = 1
        filtered_offers = []
        while len(filtered_offers) == 0:
            filtered_offers = [x for x in self.utility_manager.all_possible_offers
                               if
                               lower_utility_threshold <= self.utility_manager.get_offer_utility(x) <= upper_utility_threshold]
            upper_utility_threshold += 0.01
            lower_utility_threshold += 0.01
        random_offer_index = randrange(0, len(filtered_offers))
        random_offer = filtered_offers[random_offer_index]
        return self.create_offer(random_offer)


class ResourceAllocationActionFactory(AbstractActionFactory):
    def factory_method(self, offer_details) -> AbstractAction:
        return Offer(offer_details, self.utility_manager.calculate_offer_for_opponent(offer_details), self.bidder)


class NormalActionFactory(AbstractActionFactory):
    def factory_method(self, offer_details) -> AbstractAction:
        return Offer(offer_details, offer_details, self.bidder)

# 169.254.189.21
