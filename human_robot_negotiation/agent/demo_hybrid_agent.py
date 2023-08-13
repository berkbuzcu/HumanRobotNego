from ctypes import util
from typing import List

from human_robot_negotiation.HANT.nego_action import AbstractAction, AbstractActionFactory
from human_robot_negotiation.HANT.utility_space import UtilitySpace
from human_robot_negotiation.agent.abstract_agent import AbstractAgent

import pandas as pd

from human_robot_negotiation.agent.agent_mood.mood_controller import MoodController

class DemoHybridAgent(AbstractAgent):
    p0: float
    p1: float
    p2: float
    p3: float
    W = {
        1: [1],
        2: [0.25, 0.75],
        3: [0.11, 0.22, 0.66],
        4: [0.05, 0.15, 0.3, 0.5],
    }
    my_last_bids: List[AbstractAction]
    last_received_bids: List[AbstractAction]
    utility_space: UtilitySpace
    action_factory: AbstractActionFactory
    
    def __init__(self, utility_space, time_controller, action_factory):
        self.utility_space = utility_space
        self.time_controller = time_controller
        self.action_factory = action_factory
        self.p0 = 0.95
        self.p1 = 0.75
        self.p2 = 0.6
        self.p3 = 0.4
        self.my_last_bids = []
        self.last_received_bids = []
        self.logs = []

        self.sensitivity_class_list = []

        self.mood_controller = MoodController(self.utility_space, self.time_controller)

    def time_based(self):
        t = self.time_controller.get_remaining_time()
        return (1 - t) * (1 - t) * self.p0 + 2 * (1 - t) * t * self.p1 + t * t * self.p2

    def behaviour_based(self):
        t = self.time_controller.get_remaining_time()

        diff = [self.utility_space.get_offer_utility(self.last_received_bids[i + 1]) - \
                self.utility_space.get_offer_utility(self.last_received_bids[i])
                for i in range(len(self.last_received_bids) - 1)]

        if len(diff) > len(self.W):
            diff = diff[-len(self.W):]

        delta = sum([u * w for u, w in zip(diff, self.W[len(diff)])])

        target_utility = self.utility_space.get_offer_utility(self.my_last_bids[-1]) - (self.p3 + self.p3 * t) * delta

        return target_utility
    
    def receive_offer(self, bid: AbstractAction, predictions, normalized_predictions):
        self.last_received_bids.append(bid)
        t = self.time_controller.get_remaining_time()
        mood = self.mood_controller.get_mood(bid)
        human_offer_utility = self.utility_space.get_offer_utility(bid)
        time_based_utility = self.time_based()
        target_utility = time_based_utility

        self.logs.append({
            "Logger": "Human",
            "Offer": bid.get_bid(perspective="Agent"),
            "Agent Utility": human_offer_utility,
            "Scaled Time": t,
            "Target Utility": 0,
            "Time Based Utility": 0,
            "Behavior Based Utility": 0,
           }
        )

        behaviour_based_utility = None
        if len(self.last_received_bids) > 2:
            behaviour_based_utility = self.behaviour_based()

            target_utility = (1. - t * t) * behaviour_based_utility + t * t * target_utility

        if target_utility <= human_offer_utility:
            return self.action_factory.create_acceptance(), "Happy"

        bid = self.action_factory.get_offer_below_utility(target_utility)
        self.my_last_bids.append(bid)
        
        print("BID: ", bid, " - util: ",  human_offer_utility)

        self.logs.append({
            "Logger": "Agent",
            "Offer": bid.get_bid(perspective="Agent"),
            "Agent Utility": self.utility_space.get_offer_utility(bid.get_bid(perspective="Agent")),
            "Scaled Time": t,
            "Target Utility": target_utility,
            "Time Based Utility": time_based_utility,
            "Behavior Based Utility": behaviour_based_utility if behaviour_based_utility else 0,
        })


        return bid, mood

    def receive_negotiation_over(self, participant_name, session_number, type):
        """
        Type: agent | human | timeout
        """
        num_of_moods = self.mood_controller.get_num_of_moods()
        df = pd.DataFrame(self.logs)
        df.to_excel(f"./Logs/demohybridagent_logs_{participant_name}_{session_number}.xlsx")

        return num_of_moods
