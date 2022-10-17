import copy
from HANT import nego_action
from agent.Agent_Mood.mood_controller import MoodController
from agent.Solver_Agent.estimated_sensitivity_calculator import (
    EstimatedSensitivityCalculator,
)

import pandas as pd


# Import helper classes.
from agent.Solver_Agent.uncertainty_module import UncertaintyModule

# Math.
import math

from typing import Tuple

from HANT.utility_space import UtilitySpace


class SolverAgent:
    def __init__(self, utility_space, time_controller, action_factory):
        self.utility_space: UtilitySpace = utility_space
        self.action_factory: nego_action.AbstractActionFactory = action_factory
        self.estimated_opponent_preference: UtilitySpace = copy.deepcopy(self.utility_space)
        self.time_controller = time_controller
        self.estimated_sensitivity_calculator: EstimatedSensitivityCalculator = EstimatedSensitivityCalculator(
            self.action_factory)

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

        #self.behavior_based = bb()
        #self.time_based = kek()
        self.uncertainty_module: UncertaintyModule = UncertaintyModule(utility_space)

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

    def time_based(self):
        t = self.time_controller.remaining_time
        return (1 - t) * (1 - t) * self.p0 + 2 * (1 - t) * t * self.p1 + t * t * self.p2

    def behaviour_based(self):
        t = self.time_controller.remaining_time

        diff = [self.utility_space.get_offer_utility(self.opponent_history[i + 1]) - self.utility_space.get_offer_utility(self.opponent_history[i])
                for i in range(len(self.opponent_history) - 1)]

        if len(diff) > len(self.W):
            diff = diff[-len(self.W):]

        '''
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
        '''
        delta = sum([u * w for u, w in zip(diff, self.W[len(diff)])])

        mu = (self.p3 + self.p3 * t)

        previous_agent_offer_utility = self.utility_space.get_offer_utility(self.agent_history[-1])

        target_utility = previous_agent_offer_utility - ((1 - (self.human_awareness ** 2)) * (mu * delta))

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

        # TODO: Fix all moods fields with valance arousal.

        human_offer_utility = self.utility_space.get_offer_utility(human_offer)
        emotion_value = 0

        self.opponent_history.append(human_offer)
        self.estimated_opponent_preference = (
            self.uncertainty_module.estimate_opponent_preferences(
                self.opponent_history)
        )

        current_time = self.time_controller.remaining_time

        time_based_target_utility = self.time_based()
        behavior_based_target_utility = 0
        behavior_based_utility = 0

        final_target_utility = time_based_target_utility

        sensitivity_class = " "
        generated_offer = self.action_factory.get_offer_below_utility(final_target_utility)

        print("time based: ", time_based_target_utility)
        print(generated_offer)
        print(self.utility_space.get_offer_utility(generated_offer))

        arousal, valance = normalized_predictions["Arousal"], normalized_predictions["Valance"]

                

        if len(self.opponent_history) > 1:
            #emotion_signed_angle = math.atan2(arousal, valance) - math.atan2(self.previous_arousal, self.previous_valance)
            #emotion_distance_delta = math.sqrt((arousal - self.previous_arousal) ** 2 + (valance - self.previous_valance) ** 2)
            #emotion_distance_delta = emotion_distance_delta if emotion_signed_angle > 0 else -emotion_distance_delta
            #self.emotion_distance += emotion_distance_delta

            delta_v = valance - self.previous_valance
            delta_a = arousal - self.previous_arousal

            max_delta = max([(delta_v, abs(delta_v)), (delta_a, abs(delta_a))], key= lambda x: x[1])[0]
            emotion_value = math.copysign(math.sqrt((arousal - self.previous_arousal) ** 2 + (valance - self.previous_valance) ** 2), max_delta)


            behavior_based_utility = self.behaviour_based()
            behavior_based_target_utility = behavior_based_utility + ((self.human_awareness ** 2) * emotion_value)
            behavior_based_target_utility = behavior_based_target_utility if behavior_based_target_utility <= 1.0 else 1.0
            final_target_utility = (1 - current_time ** 2) * behavior_based_target_utility + (current_time ** 2) * time_based_target_utility

            print("Final: ", final_target_utility, "Behavior: ", behavior_based_target_utility, "Time: ", current_time, time_based_target_utility)

            if len(self.opponent_history) > 8:
                # Calculate awareness based on estimated opponent preference and utility space.
                self.human_awareness = (
                    self.estimated_sensitivity_calculator.get_human_awareness(
                        self.utility_space,
                        self.estimated_opponent_preference,
                        self.agent_history,
                        self.opponent_history,
                    )
                )
                # Get sensitivity class and update parameters with that.
                sensitivity_class_index = (
                    self.estimated_sensitivity_calculator.get_sensitivity_index(
                        self.utility_space,
                        self.estimated_opponent_preference,
                        self.opponent_history,
                    )
                )

                sensitivity_class = self.sensitivity_class[sensitivity_class_index]

                self.update_with_sensitivity_class(sensitivity_class)
                # Calculate nash offer based on estimated opponent preference.

                generated_offer = self.action_factory.get_offer_below_utility(final_target_utility)
                generated_offer_utility = self.utility_space.get_offer_utility(generated_offer)
                
        self.previous_arousal = arousal
        self.previous_valance = valance

        self.sensitivity_class_list.append(sensitivity_class)
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
            "Final Utility": final_target_utility,
            "Behavior Based Final": behavior_based_target_utility,
            "Behavior Based": behavior_based_utility,
            "Time Based": time_based_target_utility,
            "PE": emotion_value,
            "PA": self.human_awareness,
            "Estimated Issue Order": self.estimated_opponent_preference.issue_weights,
            "Estimated Value Order": self.estimated_opponent_preference.issue_value_evaluation,
            "Estimated Bid Utility": self.estimated_opponent_preference.get_offer_utility(human_offer),
            "Predictions": predictions,
            "Normalized Predictions": normalized_predictions
           }
        )

        self.logs.append({
            "Logger": "Agent",
            "Offer": generated_offer.get_bid(),
            "Agent Utility": generated_offer_utility,
            "Scaled Time": current_time,
            "Final Utility": final_target_utility,
            "Behavior Based Final": behavior_based_target_utility,
            "Behavior Based": behavior_based_utility,
            "Time Based": time_based_target_utility,
            "PE": emotion_value,
            "PA": self.human_awareness,
            "Estimated Issue Order": self.estimated_opponent_preference.issue_weights,
            "Estimated Value Order": self.estimated_opponent_preference.issue_value_evaluation,
            "Estimated Bid Utility": self.estimated_opponent_preference.get_offer_utility(generated_offer),
            "Predictions": predictions,
            "Normalized Predictions": normalized_predictions
        })
        print("ITEM SENT: ", self.agent_history[-1], " - utility: ", generated_offer_utility)
        return self.agent_history[-1], mood


    def update_with_sensitivity_class(self, sensitivity_class):
        if (sensitivity_class == "Fortunate" and self.previous_sensitivity_class != "Fortunate"):
            p1 = self.p1
            p1 = p1 - 0.2
            self.p1 = p1
        elif (
                sensitivity_class == "Standart" and self.previous_sensitivity_class != "Standart"):
            pass
        elif (sensitivity_class == "Silent" and self.previous_sensitivity_class != "Silent"):
            pass
        elif (sensitivity_class == "Selfish" and self.previous_sensitivity_class != "Selfish"):
            self.p3 = 1.5
        elif (sensitivity_class == "Concession" and self.previous_sensitivity_class != "Concession"):
            p1 = self.p1
            p2 = self.p2
            p1 = p1 + 0.2
            p2 = p2 + 0.2
            self.p1 = p1
            self.p2 = p2

        self.previous_sensitivity_class = sensitivity_class

    def receive_negotiation_over(self, participant_name, session_number, type):
        """
        Type: agent | human | timeout
        """
        num_of_moods = self.mood_controller.get_num_of_moods()
        df = pd.DataFrame(self.logs)
        df.to_excel(f"./Logs/solver_logs_{participant_name}_{session_number}.csv")

        return num_of_moods
