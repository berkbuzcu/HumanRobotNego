from human_robot_negotiation.HANT import nego_action
from human_robot_negotiation.HANT.nego_action import Accept, Offer
from human_robot_negotiation.agent.agent_strategy.babt import BABT
from human_robot_negotiation.agent.agent_mood.mood_controller import MoodController
from human_robot_negotiation.HANT.utility_space import UtilitySpace
from human_robot_negotiation.agent.abstract_agent import AbstractAgent


class MimicAgent:
    def __init__(self, utility_space, time_controller):
        self.utility_space = utility_space
        self.time_controller = time_controller
        self.opponent_previous_offer_utility = (
            -1
        )  # User's previous offer point for agent.
        self.BABT = BABT(self.utility_space)
        self.emotion_controller = MoodController(
            self.utility_space, self.time_controller
        )

    def receive_offer(self, human_offer):
        """
        This function is called when the agent receives offer.
        """
        # Get current time.
        current_time = self.time_controller.get_current_time()
        print("Current time:", current_time)
        # Generate offer based on opponent's offer and time.
        generated_offer = self.BABT.generate_offer(human_offer, current_time)
        # Get lower threshold for 'mild' emotion, it is sent if the opponent's offer utility is close to generated offer's 90%.
        threshold = self.utility_space.get_offer_utility(generated_offer) * 0.9
        emotion = self.emotion_controller.get_emotion(human_offer, threshold)
        self.opponent_previous_offer_utility = self.utility_space.get_offer_utility(
            human_offer
        )
        print("Human offer utility:", self.utility_space.get_offer_utility(human_offer))
        if self.utility_space.get_offer_utility(
            generated_offer
        ) < self.utility_space.get_offer_utility(human_offer):
            return nego_action.Accept("Agent"), "accept"
        else:
            return nego_action.Offer(generated_offer), emotion

    def receive_accept(self, human_action):
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
