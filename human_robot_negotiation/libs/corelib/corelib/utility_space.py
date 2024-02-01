from xml.dom.minidom import parse
import xml.dom.minidom
import itertools
import math
import corelib.nego_action as nego_action
import json


class UtilitySpace:
    def __init__(self, profile: dict):
        # Role weights of the agent. {issuename: issueweight, ....} etc.
        self.issue_weights = {}
        # Issue's value evaluations.  { "Apple": {0: 0.3, 1: 0.2}, "Banana": {0: 0.2, 1: 0.7} } etc.
        self.issue_value_evaluation = {}
        # Keep every issue's values in a dictionary.
        # {"Apple": ["0", "1", "2"...], "accomodation": ["Camp", "Tent"]}
        self.issue_values_list = {}
        # Issue name list.
        self.issue_names = []
        # Issues max count list for each issue.
        self.issue_max_counts = {}
        # Call the role weight function for complete the weight dictionary.
        # SUB-SUB dictionary. ie: {"Apple": {"0": 0, "1", 0.25...}, "accomodation": {"hotel": 1, "tent": 0.75...}}

        # Generate all possible offers.
        self.__generate_all_possible_offers()
        self.grid = [[(str(key).title(), "black") for key in value_dict.keys()] for value_dict in
                     self.issue_value_evaluation.values()]

        self.indices = {}
        for issue_idx, (issue, values) in enumerate(self.issue_value_evaluation.items()):
            for value_idx, value in enumerate(values):
                issue_value_key = f"{issue}_{value}"
                self.indices[issue_value_key] = (issue_idx, value_idx)

    def __generate_all_possible_offers(self):
        """
        Generate all possible offers and utilities in the ascending order.
        """
        self.all_possible_offers = [dict(zip(self.issue_names, item)) for item in
                                    itertools.product(*self.issue_values_list.values())]
        self.__all_possible_offers_utilities = [self.get_offer_utility(offer) for offer in self.all_possible_offers]

    def get_all_possible_offers_utilities(self):
        return self.__all_possible_offers_utilities

    def get_offer_utility(self, offer) -> float:
        offer_utility = 0
        if isinstance(offer, nego_action.Offer):
            offer = offer.get_bid()

        for issue_name, item in offer.items():
            issue_weight = self.issue_weights[str(issue_name).lower()]
            item_weight = self.issue_value_evaluation[str(issue_name).lower()][str(item).lower()]
            offer_utility += issue_weight * item_weight

        return round(offer_utility, 6)

    def get_domain_type(self):
        return self.domain_type

    def get_2d_ranked_grid_colored(self):
        return self.grid

    def get_value_coord(self, value):
        return self.indices[str(value)]

    def to_json(self):
        ...

    def calculate_offer_for_opponent(self, offer):
        opponent_offer = {}

        for issue_name, offered_amount in offer.items():
            # Get max count of the issue.
            issue_max_count = self.issue_max_counts[issue_name]
            # Calculate leftover for the opponent of iterating issue.
            left_count = issue_max_count - int(offered_amount)
            opponent_offer[issue_name] = str(left_count)
        return opponent_offer
