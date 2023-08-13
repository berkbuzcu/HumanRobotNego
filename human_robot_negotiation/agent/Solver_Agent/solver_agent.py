from human_robot_negotiation.HANT.nego_action import Offer, Accept, AbstractActionFactory
from human_robot_negotiation.HANT.utility_space import UtilitySpace

from human_robot_negotiation.agent.abstract_agent import AbstractAgent
from human_robot_negotiation.agent.agent_mood.mood_controller import MoodController
from human_robot_negotiation.agent.solver_agent.uncertainty_module import UncertaintyModule

from logger import LoggerNew

import typing as t
import math
import copy

from human_robot_negotiation import CONFIG_DIR

from sklearn.cluster import KMeans
import numpy as np
import json
from collections import OrderedDict
from sklearn.utils._openmp_helpers import _openmp_effective_n_threads

class EstimatedSensitivityCalculator:
	def __init__(self):
		with open(CONFIG_DIR / "solver_kmeans.json") as f:
			jsonData = json.load(f)
			self.kmeans = KMeans().fit(np.random.rand(10,6))
			self.kmeans._n_threads = _openmp_effective_n_threads()
			self.kmeans.cluster_centers_ = np.asarray(jsonData["centers"])
			self.kmeans.labels_ = np.asarray(jsonData["labels"])
			self.kmeans.n_iter_ = jsonData["n_iter"]
			self.kmeans.inertia_ = jsonData["inertia"]

	def get_opponent_moves_list(self, target_preference_profile, opponent_preference_profile, target_history):
		"""
			Gets preference profiles of both sides and given offers by target as input. Can calculate for both agent and opponent based on given input.
			Input -> target_preference_profile (to be calculated, can be either human or agent), opponent_preference_profile, target_history (offer giver side's offers)
			Returns list of moves so, the last one is the newest move.
		"""
		# Keep opponent bids utility list.
		human_bid_utility_list = []
		# Keep target's bids utility list.
		target_bid_utility_list = []
		# Iterate target's history.
		for offer in target_history:
			# Calculate offer's utility for opponent.
			opp_bid_utility = opponent_preference_profile.get_offer_utility(offer.get_bid(perspective="Human"))
			# Calculate offer's utility for target.
			target_bid_utility = target_preference_profile.get_offer_utility(offer.get_bid(perspective="Agent"))
			# Add opponent's utility to the list.
			human_bid_utility_list.append(opp_bid_utility)
			# Add target's utility to the list.
			target_bid_utility_list.append(target_bid_utility)

		# Keep target's moves in the list.
		target_move_list = []
		# Iterate through all offers.
		for i in range(len(target_history) - 1):
			# Calculate moves between 2 offers.
			if abs(target_bid_utility_list[i + 1] - target_bid_utility_list[i]) == 0 and abs(human_bid_utility_list[i + 1] - human_bid_utility_list[i]) == 0:
				target_move_list.append("silent")
			elif abs(target_bid_utility_list[i + 1] - target_bid_utility_list[i]) == 0 and abs(human_bid_utility_list[i + 1] - human_bid_utility_list[i]) > 0:
				target_move_list.append("nice")
			elif target_bid_utility_list[i + 1] - target_bid_utility_list[i] > 0 and human_bid_utility_list[i + 1] - human_bid_utility_list[i] > 0:
				target_move_list.append("fortunate")
			elif target_bid_utility_list[i + 1] - target_bid_utility_list[i] < 0 and human_bid_utility_list[i + 1] - human_bid_utility_list[i] < 0:
				target_move_list.append("unfortunate")
			elif target_bid_utility_list[i + 1] - target_bid_utility_list[i] < 0 and human_bid_utility_list[i + 1] - human_bid_utility_list[i] > 0 :
				target_move_list.append("concession")
			else:
				target_move_list.append("selfish")

		# Return target's move list as REVERSED.
		return list( target_move_list )


	def get_sensitivity_rate(self, target_move_list: t.List[str]):
		"""
			Get move list of the target (to be calculated) as input.
			Return sensitivity rate as dictionary of each move.
		"""
		# Keep rates as a dictionary.
		sensitivity_rate_dict = {"silent": 0.0, "nice": 0.0, "fortunate": 0.0, "unfortunate": 0.0, "concession": 0.0, "selfish": 0.0}
		# Iterate every move in the list.
		for move in target_move_list:
			# Update Sensitivity dict of that move by 1 / total_move_number.
			sensitivity_rate_dict[move] += 1.0 / len(target_move_list)
		# Return the final dictionary.
		return sensitivity_rate_dict

	def get_human_awareness(self, agent_preference_profile, human_preference_profile, agentHistory, humanHistory):
		"""
			Get target and opponent history and preference profiles as input.
			Returns the awareness score of the human.
		"""
		# Human's moves list and agent's moves list for their own offers.
		human_moves_list = self.get_opponent_moves_list(human_preference_profile, agent_preference_profile, humanHistory)
		agent_moves_list = self.get_opponent_moves_list(agent_preference_profile, human_preference_profile, agentHistory)

		# Initialize human's awareness.
		human_awareness = 0
		# total agent's changed move count.
		count = 0
		# Calculate human's awareness by iterating and looking differences between offer utilities for both agent and human. Since human is the first offer giver start from index 1.
		for i in range(1, len(human_moves_list) - 1):
			if (agent_moves_list[i] != agent_moves_list[i - 1]):
				count += 1
			if (human_moves_list[i + 1] != human_moves_list[i]) and (agent_moves_list[i] != agent_moves_list[i - 1]):
				# If both sides has changes, update the human's awareness by 1 / total_move_number - 1.
				human_awareness += 1

		try:
			human_awareness = human_awareness / (count * 1.0)
		except:
			human_awareness = 0
		# Return human's awareness.
		# print("awareness:", human_awareness)
		# Return human's awareness.
		if human_awareness > 0.75:
			human_awareness = 0.75
		if human_awareness < 0.25:
			human_awareness = 0.25

		return human_awareness

	def get_sensitivity_index(self, target_preference_profile: UtilitySpace, opponent_preference_profile: UtilitySpace, target_history: t.List[Offer]):
		"""
			Get sensitivity class of opponent as index number.
		"""
		move_list = self.get_opponent_moves_list(target_preference_profile, opponent_preference_profile, target_history)

		sensitivity_rate_dict = self.get_sensitivity_rate(move_list)

		sensitivity_vector = np.array([[sensitivity_rate_dict["silent"], sensitivity_rate_dict["nice"], sensitivity_rate_dict["fortunate"], sensitivity_rate_dict["unfortunate"], sensitivity_rate_dict["concession"], sensitivity_rate_dict["selfish"]]])
		return self.kmeans.predict(sensitivity_vector)[0]	


class SolverAgent(AbstractAgent):
	def __init__(self, utility_space, time_controller, action_factory):
		self.utility_space: UtilitySpace = utility_space
		self.estimated_opponent_preference: UtilitySpace = copy.deepcopy(self.utility_space)
		self.action_factory: AbstractActionFactory = action_factory
		self.time_controller = time_controller
		self.estimated_sensitivity_calculator = EstimatedSensitivityCalculator()
		self.uncertainty_module: UncertaintyModule = UncertaintyModule(utility_space)

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

		self.bid_frequencies = {}
		self.delta_multiplier = 1

	def time_based(self, t):
		return (1 - t) * (1 - t) * self.p0 + 2 * (1 - t) * t * self.p1 + t * t * self.p2

	def behaviour_based(self):
		t = self.time_controller.get_remaining_time()

		diff = [self.utility_space.get_offer_utility(self.opponent_history[i + 1]) - self.utility_space.get_offer_utility(self.opponent_history[i])
				for i in range(len(self.opponent_history) - 1)]

		if len(diff) > len(self.W):
			diff = diff[-len(self.W):]

		delta = sum([u * w for u, w in zip(diff, self.W[len(diff)])]) * self.delta_multiplier

		mu = (self.p3 + self.p3 * t)

		previous_agent_offer_utility = self.utility_space.get_offer_utility(self.agent_history[-1])

		target_utility = previous_agent_offer_utility - ((1 - (self.human_awareness ** 2)) * (mu * delta))

		print("BB TARGET: ", target_utility, previous_agent_offer_utility, mu, delta)

		return target_utility

	def check_acceptance(self, final_target_utility, human_offer_utility) -> t.Tuple[Accept, str]:
		if final_target_utility < human_offer_utility:
			self.my_prev_util = final_target_utility
			# self.agent_history.append(self.action_factory.get_offer_below_utility(final_target_utility))

			return True, (Accept(), "Happy")

		return False, ()

	def receive_offer(self, human_offer: Offer, predictions: t.Dict[str, float], normalized_predictions: t.Dict[str, float]) -> t.Tuple[Offer, str]:
		"""
		This function is called when the agent receives offer with ***mood_recording=True and also uses sensitivity class.
		"""

		human_offer_utility = self.utility_space.get_offer_utility(human_offer.get_bid(perspective="Agent"))
		emotion_value = 0

		self.opponent_history.append(human_offer)

		current_time = self.time_controller.get_remaining_time()
		time_based_target_utility = self.time_based(current_time)

		behavior_based_target_utility = 0
		behavior_based_utility = 0

		final_target_utility = time_based_target_utility
		arousal, valance = normalized_predictions["Arousal"], normalized_predictions["Valance"]
		sensitivity_class = ""
		
		if len(self.opponent_history) > 1:				
			delta_v = valance - self.previous_valance
			delta_a = arousal - self.previous_arousal

			max_delta = max([(delta_v, abs(delta_v)), (delta_a, abs(delta_a))], key= lambda x: x[1])[0]
			emotion_value = math.copysign(math.sqrt((arousal - self.previous_arousal) ** 2 + (valance - self.previous_valance) ** 2), max_delta)

			behavior_based_utility = self.behaviour_based()
			behavior_based_target_utility = behavior_based_utility + ((self.human_awareness ** 2) * emotion_value)
			behavior_based_target_utility = behavior_based_target_utility if behavior_based_target_utility <= 1.0 else 1.0
			final_target_utility = (1 - current_time ** 2) * behavior_based_target_utility + (current_time ** 2) * time_based_target_utility
			
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


		generated_offer = self.action_factory.get_offer_below_utility(final_target_utility)

		self.previous_arousal = arousal
		self.previous_valance = valance
		
		generated_offer_utility = self.utility_space.get_offer_utility(generated_offer)
		self.my_prev_util = generated_offer_utility
		
		if generated_offer_utility < human_offer_utility:
			mood = "Happy"
			self.agent_history.append(generated_offer)
			self.agent_history.append(Accept())

		else:
			mood = self.mood_controller.get_mood(human_offer.get_bid(perspective="Agent"))
			self.agent_history.append(generated_offer)

		LoggerNew.log_solver({
			"logger": "Human",
			"offer": human_offer.get_bid(perspective="Agent"),
			"agent_utility": human_offer_utility,
			"scaled_time": current_time,
			"behavior_based": behavior_based_utility,
			"behavior_based_final": behavior_based_target_utility,
			"pe": emotion_value,
			"pa": self.human_awareness,
			"time_based": time_based_target_utility,
			"final_utility": final_target_utility,
			"predictions": predictions,
			"normalized_predictions": normalized_predictions,
            "sensitivity_class": sensitivity_class
		   })

		LoggerNew.log_solver({
			"logger": "Agent",
			"offer": generated_offer.get_bid(perspective="Agent"),
			"agent_utility": generated_offer_utility,
			"scaled_time": current_time,
			"behavior_based": behavior_based_utility,
			"behavior_based_final": behavior_based_target_utility,
			"pe": emotion_value,
			"pa": self.human_awareness,
			"time_based": time_based_target_utility,
			"final_utility": final_target_utility,
			"predictions": predictions,
			"normalized_predictions": normalized_predictions,
			"sensitivity_class": sensitivity_class
		})

		print("T: ", current_time)
		print("Final: ", final_target_utility, " Behavior Based: ", behavior_based_target_utility, " Time Based: ", time_based_target_utility)

		print("ITEM SENT: ", self.agent_history[-1], " - UTIL: ", generated_offer_utility)
		return self.agent_history[-1], mood

	def receive_negotiation_over(self, participant_name: str, session_number: str, type: str):
		"""
		Type: agent | human | timeout
		"""
		num_of_moods = self.mood_controller.get_num_of_moods()
		return num_of_moods
	
	def update_with_sensitivity_class(self, sensitivity_class):
		if sensitivity_class == "Fortunate" and self.previous_sensitivity_class != "Fortunate":
			self.p1 = self.p1 - 0.2
		elif sensitivity_class == "Standart" and self.previous_sensitivity_class != "Standart":
			pass
		elif sensitivity_class == "Silent" and self.previous_sensitivity_class != "Silent":
			pass
		elif sensitivity_class == "Selfish" and self.previous_sensitivity_class != "Selfish":
			self.delta_multiplier = 1.5 
		elif sensitivity_class == "Concession" and self.previous_sensitivity_class != "Concession":
			self.p1 = self.p1 + 0.2
			self.p2 = self.p2 + 0.2
		self.previous_sensitivity_class = sensitivity_class