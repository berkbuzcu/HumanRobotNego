import random
from human_robot_negotiation.HANT.utility_space import UtilitySpace

# Behavior-dependent adaptive bidding tactic.


class BABT:
    def __init__(self, utility_space):
        self.previous_human_offer_utility = (
            -1
        )  # Human's previous offer utility for agent.
        self.previous_agent_offer_utility = (
            -1
        )  # Agent's generated offer utility for itself.
        self.previous_agent_offer = -1  # Agent's previous generated offer for itself.
        self.offer_difference = -1
        self.time_var = 0.5
        self.utility_space = utility_space

    # Set offer constant before generating offer.
    def set_offer_constant(self, time):
        self.offer_constant = self.time_var + time * 0.5

    # First return empty array for user, then start to compare with previous user offer and generate the closest to the difference.
    def generate_offer(self, human_offer, time):
        self.set_offer_constant(time)
        human_offer_utility = self.utility_space.get_offer_utility(human_offer)
        if self.previous_human_offer_utility == -1:
            self.previous_human_offer_utility = human_offer_utility
            self.previous_agent_offer = self.utility_space.get_offer_between_utility(
                0.95, 0.95
            )
            self.previous_agent_offer_utility = self.utility_space.get_offer_utility(
                self.previous_agent_offer
            )
            return self.previous_agent_offer
        elif human_offer_utility - self.previous_human_offer_utility == 0:
            return self.previous_agent_offer
        else:
            offer_difference = (
                human_offer_utility - self.previous_human_offer_utility
            ) * self.offer_constant
            target_utility = float(self.previous_agent_offer_utility - offer_difference)
            self.previous_agent_offer = self.utility_space.get_offer_between_utility(
                target_utility, target_utility
            )
            self.previous_human_offer_utility = human_offer_utility
            self.previous_agent_offer_utility = self.utility_space.get_offer_utility(
                self.previous_agent_offer
            )
            self.offer_difference = offer_difference
            return self.previous_agent_offer
