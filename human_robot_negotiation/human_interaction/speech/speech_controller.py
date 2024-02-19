import typing as t
from corelib import nego_action


class SpeechController:
    def __init__(
            self, offer_classifier
    ):
        self.previous_user_action = None
        self.human_sentences = []
        self.offer_classifier = offer_classifier
        self.total_user_input = ""

    def get_human_action(self, user_input) -> t.Tuple[nego_action.Offer, bool, str]:
        """
        Listen the user offer, then select keywords from sentence, check similarities and return what's left to the agent from user.
        """
        offer_done = False

        self.total_user_input += str(user_input).strip() + " "
        user_action, offer_done = self.offer_classifier.get_offer_and_arguments(str(self.total_user_input))

        self.previous_user_action = user_action

        self.previous_user_action = None
        self.human_sentences.append(self.total_user_input)

        # status, offer_done, offer_string, offer_utility, time, human_message
        # status: ["Caduceus is listening", "Caduceus' turn", "Agreement is reached"]
        # offer_done: True, False
        # time: current time (may switch to time controller)
        # offer_utility: calculated offer's utility thus far
        # human_message: message from the human
        # status, offer_done, offer_string, offer_utility, human_message, human_action
        if offer_done:
            self.total_user_input = ""

        return user_action, offer_done, self.total_user_input
