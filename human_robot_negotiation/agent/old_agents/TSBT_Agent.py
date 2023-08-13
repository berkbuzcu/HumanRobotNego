from human_robot_negotiation.HANT import nego_action
from human_robot_negotiation.HANT.nego_action import Accept, Offer
from human_robot_negotiation.agent.agent_strategy.tsbt import TSBT
from human_robot_negotiation.agent.agent_mood.mood_controller import MoodController
from human_robot_negotiation.HANT.utility_space import UtilitySpace
from human_robot_negotiation.agent.abstract_agent import AbstractAgent


class TSBTAgent:
    def __init__(self, utility_space, time_controller):
        self.utility_space = utility_space
        self.time_controller = time_controller
        self.opponent_previous_offer_utility = (
            -1
        )  # User's previous offer point for agent.
        self.TSBT = TSBT(self.utility_space)

    def receive_offer(self, human_offer):
        current_time = self.time_controller.get_current_time()
        generated_offer = self.TSBT.generate_offer(current_time)
        emotion = self.mood_controller.get_emotion(
            human_offer, self.BABT.lower_threshold
        )
        if self.utility_space.get_offer_utility(
            generated_offer
        ) < self.utility_space.get_offer_utility(human_bid):
            return nego_action.Accept("Agent"), "accept"
        else:
            self.opponent_previous_offer_utility = self.utility_space.get_offer_utility(
                human_bid
            )
            return nego_action.Offer(generated_offer), emotion

    def receive_accept(self, humanAction):
        """
        It is called at the end of the acceptance.
        """
        num_of_emotions = self.emotion_controller.get_num_of_emotions()
        return num_of_emotions

    def receive_end_of_deadline(self):
        """
        It is called when negotiation ends without an agreement.
        """
        num_of_emotions = self.emotion_controller.get_num_of_emotions()
        return num_of_emotions
