import copy
from human_robot_negotiation.HANT import nego_action
from human_robot_negotiation.agent.agent_mood.mood_controller import MoodController

import pandas as pd


# Import helper classes.
# Math.
import math

from typing import Tuple

from human_robot_negotiation.HANT.utility_space import UtilitySpace


class SolverAgent:
    def __init__(self, utility_space, time_controller, action_factory):
        self.utility_space: UtilitySpace = utility_space
        self.action_factory: nego_action.AbstractActionFactory = action_factory
        self.time_controller = time_controller

        self.agent_history = []
        self.opponent_history = []
        self.sensitivity_class = {
            0: "Standart",
            1: "Silent",
            2: "Selfish",
            3: "Fortunate",
            4: "Concession",
        }
        self.mood_evaluations = {
            "Surprise": 0.33,
            "Happiness": 0.165,
            "Neutral": 0,
            "Disgust": 0,
            "Fear": 0,
            "Anger": -0.165,
            "Sadness": -0.33,
        }
        self.human_awareness = 0.5  # Will fix.
        self.silent_nash_index = 0  #

        self.emotion_distance = 0

        self.sensitivity_class_list = []

        self.my_prev_util = 0
        
        # Keep previous arousal and valance.
        self.previous_arousal = 0
        self.previous_valance = 0

        # Initialize mood controller.
        self.mood_controller = MoodController(
            self.utility_space, self.time_controller
        )
        # Initialize previous sensitivity class as none.
        self.previous_sensitivity_class = None

        self.p0 = 0.9
        self.p1 = 0.7
        self.p2 = 0.4
        self.p3 = 0.5

        self.W = {
            1: [1],
            2: [0.25, 0.75],
            3: [0.11, 0.22, 0.66],
            4: [0.05, 0.15, 0.3, 0.5],
        }

        self.logs = []

        self.bid_frequencies = {}

    def time_based(self, t):
        return (1 - t) * (1 - t) * self.p0 + 2 * (1 - t) * t * self.p1 + t * t * self.p2

    def behaviour_based(self):
        t = self.time_controller.remaining_time

        diff = [self.utility_space.get_offer_utility(self.opponent_history[i + 1]) - self.utility_space.get_offer_utility(self.opponent_history[i])
                for i in range(len(self.opponent_history) - 1)]

        if len(diff) > len(self.W):
            diff = diff[-len(self.W):]

        delta = sum([u * w for u, w in zip(diff, self.W[len(diff)])])

        mu = (self.p3 + self.p3 * t)

        previous_agent_offer_utility = self.utility_space.get_offer_utility(self.agent_history[-1])

        target_utility = previous_agent_offer_utility - ((1 - (self.human_awareness ** 2)) * (mu * delta))

        print("BB TARGET: ", target_utility, previous_agent_offer_utility, mu, delta)

        return target_utility

    def check_acceptance(self, final_target_utility, human_offer_utility) -> Tuple[nego_action.Accept, str]:
        if final_target_utility < human_offer_utility:
            self.my_prev_util = final_target_utility
            # self.agent_history.append(self.action_factory.get_offer_below_utility(final_target_utility))

            return True, (nego_action.Accept(), "Happy")

        return False, ()

    def receive_offer(self, human_offer: nego_action.Offer, predictions, normalized_predictions):
        """
        This function is called when the agent receives offer with ***mood_recording=True and also uses sensitivity class.
        """

        human_offer_utility = self.utility_space.get_offer_utility(human_offer)
        emotion_value = 0

        self.opponent_history.append(human_offer)

        current_time = self.time_controller.remaining_time
        time_based_target_utility = self.time_based(current_time)

        behavior_based_target_utility = 0
        behavior_based_utility = 0

        final_target_utility = time_based_target_utility
        arousal, valance = normalized_predictions["Arousal"], normalized_predictions["Valance"]
        
        if len(self.opponent_history) > 1:
            delta_v = valance - self.previous_valance
            delta_a = arousal - self.previous_arousal

            max_delta = max([(delta_v, abs(delta_v)), (delta_a, abs(delta_a))], key= lambda x: x[1])[0]
            emotion_value = math.copysign(math.sqrt((arousal - self.previous_arousal) ** 2 + (valance - self.previous_valance) ** 2), max_delta)

            behavior_based_utility = self.behaviour_based()
            behavior_based_target_utility = behavior_based_utility + ((self.human_awareness ** 2) * emotion_value)
            behavior_based_target_utility = behavior_based_target_utility if behavior_based_target_utility <= 1.0 else 1.0
            final_target_utility = (1 - current_time ** 2) * behavior_based_target_utility + (current_time ** 2) * time_based_target_utility

        generated_offer = self.action_factory.get_offer_below_utility(final_target_utility)

        self.previous_arousal = arousal
        self.previous_valance = valance
        
        generated_offer_utility = self.utility_space.get_offer_utility(generated_offer)
        self.my_prev_util = generated_offer_utility
        
        if generated_offer_utility < human_offer_utility:
            mood = "Happy"
            self.agent_history.append(generated_offer)
            self.agent_history.append(nego_action.Accept())

        else:
            mood = self.mood_controller.get_mood(human_offer)
            self.agent_history.append(generated_offer)

        self.logs.append({
            "Logger": "Human",
            "Offer": human_offer.get_bid(),
            "Agent Utility": human_offer_utility,
            "Scaled Time": current_time,
            "Behavior Based": behavior_based_utility,
            "Behavior Based Final": behavior_based_target_utility,
            "PE": emotion_value,
            "PA": self.human_awareness,
            "Time Based": time_based_target_utility,
            "Final Utility": final_target_utility,
            "Predictions": predictions,
            "Normalized Predictions": normalized_predictions
           }
        )

        self.logs.append({
            "Logger": "Agent",
            "Offer": generated_offer.get_bid(),
            "Agent Utility": generated_offer_utility,
            "Scaled Time": current_time,
            "Behavior Based": behavior_based_utility,
            "Behavior Based Final": behavior_based_target_utility,
            "PE": emotion_value,
            "PA": self.human_awareness,
            "Time Based": time_based_target_utility,
            "Final Utility": final_target_utility,
            "Predictions": predictions,
            "Normalized Predictions": normalized_predictions
        })

        print("T: ", current_time)
        print("Final: ", final_target_utility, " Behavior Based: ", behavior_based_target_utility, " Time Based: ", time_based_target_utility)

        print("ITEM SENT: ", self.agent_history[-1], " - UTIL: ", generated_offer_utility)
        return self.agent_history[-1], mood

    def receive_negotiation_over(self, participant_name, session_number, type):
        """
        Type: agent | human | timeout
        """
        num_of_moods = self.mood_controller.get_num_of_moods()
        df = pd.DataFrame(self.logs)
        df.to_excel(f"./Logs/solver_logs_{participant_name}_{session_number}.xlsx")

        return num_of_moods
