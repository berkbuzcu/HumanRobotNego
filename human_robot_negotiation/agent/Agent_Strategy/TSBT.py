import random
from human_robot_negotiation.HANT.utility_space import UtilitySpace

# Time-dependent stochastic bidding tactic.


class TSBT:
    def __init__(self, utility_space):
        self.lower_max = 0.94
        self.upper_max = 1
        self.lower_min = 0.4
        self.upper_min = 0.7
        self.lower_curvature = 0.5
        self.upper_curvature = 0.9
        self.is_first_offer = True
        self.utility_space = utility_space

    # Generate offer between thresholds. If there's no possible offer between thresholds, return empty offer to the user.
    def generate_offer(self, time):
        self.set_thresholds(time)
        offer = self.utility_space.get_offer_between_utility(
            self.lower_threshold, self.upper_threshold
        )
        return offer

    # Set time based upper and lower thresholds.
    def set_thresholds(self, time):
        self.lower_threshold = float(
            ((1 - time) * (1 - time) * self.lower_max)
            + (2 * (1 - time) * time * self.lower_curvature)
            + (time * time * self.lower_min)
        )
        self.upper_threshold = float(
            ((1 - time) * (1 - time) * self.upper_max)
            + (2 * (1 - time) * time * self.upper_curvature)
            + (time * time * self.upper_min)
        )
