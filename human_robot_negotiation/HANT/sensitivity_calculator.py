from sklearn.cluster import KMeans
import numpy as np
import pickle as pkl


class SensitivityCalculator:
    """
    This class calculates the sensitivity for given preference profiles and history of the target.
    """

    def get_single_move(self, self_utility, prev_self_utility, opponent_utility, prev_opponent_utility):
        if abs(self_utility - prev_self_utility) == 0 and \
            abs(opponent_utility - prev_opponent_utility) == 0:
            return "silent"
        elif abs( self_utility - prev_self_utility) == 0 and \
             (opponent_utility -  prev_opponent_utility > 0):
            return "nice"
        elif (self_utility - prev_self_utility > 0) and \
             (opponent_utility -  prev_opponent_utility > 0):
            return "fortunate"
        elif (self_utility - prev_self_utility < 0) and \
             (opponent_utility -  prev_opponent_utility < 0):
            return "unfortunate"
        elif (self_utility - prev_self_utility < 0) and \
             (opponent_utility -  prev_opponent_utility > 0):
            return "concession"
        else:
            return "selfish"

    def get_target_move_list(self, target_utility_list, opponent_utility_list):
        """
        Gets utilities of both sides as input. Can calculate for both agent and opponent based on given input.
        Returns list of moves.
        """

        # Keep target's moves in the list.
        target_move_list = [""]
        # Iterate through all offers.
        for i in range(len(target_utility_list) - 1):
            # Calculate moves between 2 offers.
            if (
                abs(target_utility_list[i + 1] - target_utility_list[i]) == 0
                and abs(opponent_utility_list[i + 1] - opponent_utility_list[i]) == 0
            ):
                target_move_list.append("silent")
            elif abs(target_utility_list[i + 1] - target_utility_list[i]) == 0 and (
                opponent_utility_list[i + 1] - opponent_utility_list[i] > 0
            ):
                target_move_list.append("nice")
            elif (target_utility_list[i + 1] - target_utility_list[i] > 0) and (
                opponent_utility_list[i + 1] - opponent_utility_list[i] > 0
            ):
                target_move_list.append("fortunate")
            elif (target_utility_list[i + 1] - target_utility_list[i] < 0) and (
                opponent_utility_list[i + 1] - opponent_utility_list[i] < 0
            ):
                target_move_list.append("unfortunate")
            elif (target_utility_list[i + 1] - target_utility_list[i] < 0) and (
                opponent_utility_list[i + 1] - opponent_utility_list[i] > 0
            ):
                target_move_list.append("concession")
            else:
                target_move_list.append("selfish")

        # Return target's move list as REVERSED.
        return target_move_list

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
        if target_move_list:
            for move_index in range(1, len(target_move_list)):
                move = target_move_list[move_index]
                # Update Sensitivity dict of that move by 1 / total_move_number.
                sensitivity_rate_dict[move] += 1.0 / (len(target_move_list) - 1)
            # Return the final dictionary.
        return sensitivity_rate_dict

    def get_human_awareness(
        self,
        agent_offer_agent_utilities,
        agent_offer_human_utilities,
        human_offer_agent_utilities,
        human_offer_human_utilities,
    ):
        """
        Get target and opponent utility lists for their offers(Human bid utility: human offers' utility for human, same goes for agent) as input.
        Returns the awareness score of the human.
        """

        # Human's moves list and agent's moves list for their own offers.
        human_moves_list = self.get_target_move_list(
            human_offer_human_utilities, human_offer_agent_utilities
        )
        agent_moves_list = self.get_target_move_list(
            agent_offer_agent_utilities, agent_offer_human_utilities
        )

        # There is an empty element at the start of the moves list. We need that for logging purposes, it is not useful here.
        human_moves_list.pop(0)
        agent_moves_list.pop(0)

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
        return human_awareness

    def get_target_turn_move(
        self,
        target_utility,
        target_previous_utility,
        opponent_utility,
        opponent_previous_utility,
    ):
        """
        Gets target's and opponent's current and previous utilities.
        Returns target's move of that turn.
        """

        # Calculate moves between 2 offers.
        if (
            abs(target_utility - target_previous_utility) == 0
            and abs(opponent_utility - opponent_previous_utility) == 0
        ):
            return "silent"
        elif (
            abs(target_utility - target_previous_utility) == 0
            and opponent_utility - opponent_previous_utility > 0
        ):
            return "nice"
        elif (
            target_utility - target_previous_utility > 0
            and opponent_utility - opponent_previous_utility > 0
        ):
            return "fortunate"
        elif (
            target_utility - target_previous_utility < 0
            and opponent_utility - opponent_previous_utility < 0
        ):
            return "unfortunate"
        elif (
            target_utility - target_previous_utility < 0
            and opponent_utility - opponent_previous_utility > 0
        ):
            return "concession"
        else:
            return "selfish"
