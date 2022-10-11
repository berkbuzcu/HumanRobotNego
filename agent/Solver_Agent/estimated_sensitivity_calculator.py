from msilib.schema import ActionText
from sklearn.cluster import KMeans
import numpy as np
import json
from collections import OrderedDict
from HANT.nego_action import AbstractActionFactory
from HANT.utility_space import UtilitySpace

from typing import List

class EstimatedSensitivityCalculator:
    """
    This class calculates the sensitivity for given preference profiles and history of the target.
    """
    action_factory: AbstractActionFactory

    def __init__(self, action_factory):
        with open("Agent/Solver_Agent/kmeans.json") as f:
            jsonData = json.load(f)
            self.kmeans = KMeans().fit(np.random.rand(10,6))
            self.kmeans.cluster_centers_ = np.asarray(jsonData["centers"])
            self.kmeans.labels_ = np.asarray(jsonData["labels"])
            self.kmeans.n_iter_ = jsonData["n_iter"]
            self.kmeans.inertia_ = jsonData["inertia"]
            self.action_factory = action_factory

    def get_opponent_moves_list(
        self, targetPreferenceProfile: UtilitySpace, opponentPreferenceProfile: UtilitySpace, targetHistory, epsilon: float = 0.03
    ):
        """
        Gets preference profiles of both sides and given offers by target as input. Can calculate for both agent and opponent based on given input.
        Input -> targetPreferenceProfile (to be calculated, can be either human or agent), opponentPreferenceProfile, targetHistory (offer giver side's offers)
        Returns list of moves so, the last one is the newest move.
        """
        # Keep opponent bids utility list.
        human_bid_utility_list = []
        # Keep target's bids utility list.
        target_bid_utility_list = []
        # Iterate target's history.
        for offer in targetHistory:
            # Calculate the offer's items for opponent. TODO: THIS IS NOT GENERIC.
            offer_to_opponent = offer.get_bid(perspective="Human")
            # Calculate offer's utility for opponent.
            opp_bid_utility = opponentPreferenceProfile.get_offer_utility(
                offer_to_opponent
            )
            # Calculate offer's utility for target.
            target_bid_utility = targetPreferenceProfile.get_offer_utility(
                offer.get_bid()
            )
            # Add opponent's utility to the list.
            human_bid_utility_list.append(opp_bid_utility)
            # Add target's utility to the list.
            target_bid_utility_list.append(target_bid_utility)

        # Keep target's moves in the list.
        target_move_list = []
        # Iterate through all offers.
        for i in range(len(targetHistory) - 1):
            # Calculate moves between 2 offers.
            if (
                abs(target_bid_utility_list[i + 1] - target_bid_utility_list[i]) < epsilon
                and abs(human_bid_utility_list[i + 1] - human_bid_utility_list[i]) < epsilon
            ):
                target_move_list.append("silent")
            elif (
                abs(target_bid_utility_list[i + 1] - target_bid_utility_list[i]) < epsilon
                and human_bid_utility_list[i + 1] - human_bid_utility_list[i] > 0
            ):
                target_move_list.append("nice")
            elif (
                target_bid_utility_list[i + 1] - target_bid_utility_list[i] > 0
                and human_bid_utility_list[i + 1] - human_bid_utility_list[i] > 0
            ):
                target_move_list.append("fortunate")
            elif (
                target_bid_utility_list[i + 1] - target_bid_utility_list[i] <= 0
                and human_bid_utility_list[i + 1] - human_bid_utility_list[i] < 0
            ):
                target_move_list.append("unfortunate")
            elif (
                target_bid_utility_list[i + 1] - target_bid_utility_list[i] < 0
                and human_bid_utility_list[i + 1] - human_bid_utility_list[i] >= 0
            ):
                target_move_list.append("concession")
            else:
                target_move_list.append("selfish")

        # Return target's move list as REVERSED.
        return list(target_move_list)

    def get_sensitivity_rate(self, target_move_list):
        """
        Get move list of the target (to be calculated) as input.
        Return sensitivity rate as dictionary of each move.
        """
        # Keep rates as a dictionary.
        sensitivity_rate_dict = {
            "silent": 0,
            "nice": 0,
            "fortunate": 0,
            "unfortunate": 0,
            "concession": 0,
            "selfish": 0,
        }
        # Iterate every move in the list.
        for move in target_move_list:
            # Update Sensitivity dict of that move by 1 / total_move_number.
            sensitivity_rate_dict[move] += 1.0 / len(target_move_list)
        # Return the final dictionary.
        return sensitivity_rate_dict

    def get_human_awareness(
        self, agentPreferenceProfile, humanPreferenceProfile, agentHistory, humanHistory
    ):
        """
        Get target and opponent history and preference profiles as input.
        Returns the awareness score of the human.
        """
        # Human's moves list and agent's moves list for their own offers.
        human_moves_list = self.get_opponent_moves_list(
            humanPreferenceProfile, agentPreferenceProfile, humanHistory
        )
        agent_moves_list = self.get_opponent_moves_list(
            agentPreferenceProfile, humanPreferenceProfile, agentHistory
        )

        # Initialize human's awareness.
        human_awareness = 0
        # total agent's changed move count.
        count = 0
        # Calculate human's awareness by iterating and looking differences between offer utilities for both agent and human. Since human is the first offer giver start from index 1.
        for i in range(1, len(human_moves_list) - 1):
            if agent_moves_list[i] != agent_moves_list[i - 1]:
                count += 1
            if (human_moves_list[i + 1] != human_moves_list[i]) and (
                agent_moves_list[i] != agent_moves_list[i - 1]
            ):
                # If both sides has changes, update the human's awareness by 1 / total_move_number - 1.
                human_awareness += 1

        try:
            human_awareness = human_awareness / (count * 1.0)
        except:
            human_awareness = 0
        # Return human's awareness.
        # print("awareness:", human_awareness)
        # Return human's awareness.
        return human_awareness

    def get_sensitivity_index(
        self, targetPreferenceProfile, opponentPreferenceProfile, targetHistory
    ):
        """
        Get sensitivity class of opponent as index number.
        """
        move_list = self.get_opponent_moves_list(
            targetPreferenceProfile, opponentPreferenceProfile, targetHistory
        )

        sensitivity_rate_dict = self.get_sensitivity_rate(move_list)

        sensitivityVector = np.array(
            [
                [
                    sensitivity_rate_dict["silent"],
                    sensitivity_rate_dict["nice"],
                    sensitivity_rate_dict["fortunate"],
                    sensitivity_rate_dict["unfortunate"],
                    sensitivity_rate_dict["concession"],
                    sensitivity_rate_dict["selfish"],
                ]
            ]
        )
        return self.kmeans.predict(sensitivityVector)[0]

    def get_nash_offers(
        self, agent_preference_profile, estimated_opponent_preference) -> List[OrderedDict]:
        nash_products = []
        agent_all_offers = agent_preference_profile.all_possible_offers[:]

        #real_nash_products = []
        #real_opponent_preference = UtilitySpace(agent_preference_profile.replace("Agent", "Human"))

        for offer in agent_all_offers:
            offer = self.action_factory.create_offer(offer)
        
            offer_to_human = offer.get_bid("Human")
            offer_utility_to_human = estimated_opponent_preference.get_offer_utility(offer_to_human)
            #real_offer_utility_to_human = real_opponent_preference.get_offer_utility(
            #    offer_to_human
            #)
            agent_offer_utility = agent_preference_profile.get_offer_utility(offer)
            nash_products.append(
                ((agent_offer_utility * offer_utility_to_human), offer.get_bid())
            )
            #real_nash_products.append(
            #    ((agent_offer_utility * real_offer_utility_to_human), offer)
            #)

        #print("nashes: ", nash_products)
        nash_products.sort(reverse=True, key=lambda x: (x[0]))
        #real_nash_products.sort(reverse=True, key=lambda x: (x[0], sum(x[1])))

        # print("nash products:", nash_products[0], nash_products[1], nash_products[2], nash_products[3])

        nash_products = list(OrderedDict(nash_products[::-1]).items())[::-1]
        #real_nash_products = list(OrderedDict(real_nash_products[::-1]).items())[::-1]

        # for nash_product in nash_products:
        # print("Nash and offer utility for agent - human:", nash_product, agent_preference_profile.get_offer_utility(nash_product[1]), estimated_opponent_preference.get_offer_utility(agent_preference_profile.calculate_offer_for_opponent(nash_product[1])))

        # for nash_product in real_nash_products:
        # print("Real Nash and offer utility for agent - human:", nash_product, agent_preference_profile.get_offer_utility(nash_product[1]), real_opponent_preference.get_offer_utility(agent_preference_profile.calculate_offer_for_opponent(nash_product[1])))
    
        return nash_products
