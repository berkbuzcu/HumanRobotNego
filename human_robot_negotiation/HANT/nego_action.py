from abc import ABC, abstractmethod
from random import randrange
import random
from unicodedata import bidirectional

from .utility_space import UtilitySpace


class AbstractAction(object):
    def __init__(self, agent_id):
        self.__bid = None
        self.__time_offered = None

    def set_time_offered(self, time):
        self.__time_offered = time

    def get_time_offered(self):
        return self.__time_offered


class Accept(AbstractAction):
    def __init__(self, acceptor="Agent"):
        self.__acceptor = acceptor

    def set_bid(self, bid):
        self.__bid = bid

    def get_acceptor(self):
        return self.__acceptor

    def get_bid(self, perspective):
        return self.__bid


class Offer(AbstractAction):
    def __init__(self, bidder_perspective, reverse_perspective, bidder="Agent"):
        self.__bidder = bidder

        #bidder = Agent | Human
        reverse_swap = {"Agent": "Human", "Human": "Agent"}
        self.__bid_perspectives = {bidder: bidder_perspective, reverse_swap[bidder]: reverse_perspective}

    def get_bidder(self):
        return self.__bidder

    def get_bid(self, perspective="Agent"):
        return self.__bid_perspectives[perspective]

    def set_bid(self, bid, perspective):
        self.__bid = bid

    def __str__(self):
        bid_str = " ".join(map(str, self.__bid_perspectives[self.__bidder].values()))
        return bid_str
    
    def __getitem__(self, issue):
        return (self.get_bid()[issue])

    def __hash__(self) -> int:
        return sum([hash(item) for item in self.get_bid().values()])

    def __eq__(self, __o: object) -> bool:
        return set(self.get_bid("Agent").values()) == set(__o.get_bid("Agent").values())


class AbstractActionFactory(ABC):
    def __init__(self, utility_manager: UtilitySpace, bidder="Agent"):
        self.utility_manager = utility_manager
        self.bidder = bidder

    @abstractmethod
    def factory_method(offer_details: dict, creator: str):
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
            filtered_offers = [x for x in self.all_possible_offers
                               if (self.utility_manager.get_offer_utility(x) >= lower_utility_threshold
                                   and self.utility_manager.get_offer_utility(x) < upper_utility_threshold
                                   )]
            upper_utility_threshold += 0.01
            lower_utility_threshold -= 0.01
        random_offer_index = randrange(0, len(filtered_offers))
        random_offer = filtered_offers[random_offer_index]
        return self.create_offer(random_offer)

    def get_offer_below_utility(self, target_utility) -> Offer:
        # Try to get lower_utility and upper boundry of the target utility that exist, 
        # if any exception happends set limits to 1 and max.
        #lower_utility = max([
        #    utility
        #    for _, utility in enumerate(
        #        self.utility_manager.get_all_possible_offers_utilities()
        #    )
        #    if target_utility >= utility
        #])
        #lower_utility = max(lower_utility, 0.4)
        #lower_utility = min(lower_utility, 0.9)

        #upper_utility = min([utility
        #                     for _, utility in enumerate(
        #                         self.utility_manager.get_all_possible_offers_utilities())
        #                     if target_utility <= utility
        #                     ])
        #upper_utility = min(upper_utility, 0.9)

        ## If the target utility is the same as upper limit return it, otherwise return lower utility threshold.
        #if target_utility == upper_utility:
        #    selected_utility = upper_utility
        #else:
        #    selected_utility = lower_utility

        # Return the offer with the most element.
        #indexes = [index
        #           for index, utility in enumerate(self.utility_manager.get_all_possible_offers_utilities())
        #           if utility == selected_utility]

        bids_utils = list(zip(self.utility_manager.all_possible_offers, self.utility_manager.get_all_possible_offers_utilities()))
        bids_utils.sort(key=lambda x: x[1], reverse=True)

        for idx, (bid, utility) in enumerate(bids_utils):
            if utility < target_utility:
                break

        offer = random.choice(bids_utils[idx:idx+3])[0]
        return self.create_offer(offer)

    def get_offer_above_utility(self, lower_utility_threshold) -> Offer:
        upper_utility_threshold = 1
        filtered_offers = []
        while len(filtered_offers) == 0:
            filtered_offers = [x for x in self.utility_manager.all_possible_offers
                               if self.utility_manager.get_offer_utility(x) >= lower_utility_threshold
                               and self.utility_manager.get_offer_utility(x) <= upper_utility_threshold]
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


#169.254.189.21