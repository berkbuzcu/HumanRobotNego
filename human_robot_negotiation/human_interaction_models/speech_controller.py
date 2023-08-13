from human_robot_negotiation.human_interaction_models.speech_to_text_streaming_beta import (
    SpeechStreamingRecognizerBeta,
)

import time

from human_robot_negotiation.HANT.nego_action import Offer
import typing as t


class SpeechController:
    def __init__(
        self, offer_classifier
    ):
        self.previous_user_action = None
        self.human_sentences = []
        self.offer_classifier = offer_classifier
        self.recognizer = SpeechStreamingRecognizerBeta(offer_classifier.domain_keywords)

    def get_human_action(self) -> t.Tuple[Offer, bool, str]:
        """
        Listen the user offer, then select keywords from sentence, check similarities and return what's left to the agent from user.
        """
        offer_done = False
        total_user_input = ""
        user_input = (
            self.recognizer.listen_and_convert_to_text()
        )
        
        # If there is no timeout.
        if str(user_input) != "timeouterror":
            total_user_input += str(user_input).strip() + " "
            user_action, offer_done = self.offer_classifier.get_offer_and_arguments(str(total_user_input))

            self.previous_user_action = user_action
        
        self.previous_user_action = None
        self.human_sentences.append(total_user_input)

        # status, offer_done, offer_string, offer_utility, time, human_message
        # status: ["Caduceus is listening", "Caduceus' turn", "Agreement is reached"]
        # offer_done: True, False
        # time: current time (may switch to time controller)
        # offer_utility: calculated offer's utility thus far
        # human_message: message from the human
        # status, offer_done, offer_string, offer_utility, human_message, human_action
        return user_action, offer_done, total_user_input


