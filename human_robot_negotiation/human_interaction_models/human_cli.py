import requests
from human_robot_negotiation.human_interaction_models.holiday_offer_classifier import HolidayOfferClassifier
from human_robot_negotiation.HANT import nego_action
from human_robot_negotiation.HANT.nego_action import Offer, Accept
from human_robot_negotiation.HANT.utility_space_controller import UtilitySpaceController
import time


class HumanCLI:
    def __init__(
        self, human_utility_space, domain_file, negotiation_gui, time_controller
    ):
        self.count = 0
        # self.sentences = ["I want 4 watermelon 3 banana 4 orange 3 apple",
        #             "I want 3 watermelon 4 banana 4 orange 4 apple",
        #             "I want 3 watermelon 4 banana 4 orange 3 apple",
        #             "I want 3 watermelon 4 banana 4 orange 2 apple",
        #             "I want 4 watermelon 3 banana 4 orange 3 apple",
        #             "I want 2 watermelon 4 banana 2 orange 4 apple",
        #             "I want 3 watermelon 2 banana 3 orange 4 apple",
        #             "I want 3 watermelon 2 banana 3 orange 3 apple",
        #             "I want 3 watermelon 1 banana 4 orange 3 apple",
        #             "I want 2 watermelon 3 banana 2 orange 2 apple",
        #             "I want 2 watermelon 3 banana 2 orange 1 apple",
        #             "I want 2 watermelon 3 banana 2 orange 0 apple",
        #             "deal"]
        self.sentences = [
            "I want all of them",
            "I want all of them except 1 banana",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them",
            "I want all of them except 1 watermelon",
            "I want one banana rest is yours",
        ]
        self.human_utility_space = human_utility_space
        self.negotiation_gui = negotiation_gui
        self.utility_space_controller = UtilitySpaceController(domain_file)
        self.time_controller = time_controller
        self.human_sentences = []

    def get_human_action(self):
        """
        Listen the user offer, then select keywords from sentence, check similarities and return what's left to the agent from user.
        """
        done = False
        total_user_input = ""
        self.negotiation_gui.update_status("Caduceus is listening")
        self.negotiation_gui.update_time(
            round(self.time_controller.get_current_time(), 2) * 600
        )
        human_offer = None
        while not done:
            offer_classifier = HolidayOfferClassifier(self.human_utility_space)
            user_input = raw_input("Enter your offer: ")

            if str(user_input) != "timeouterror":
                total_user_input += str(user_input).strip() + " "
                print("User input", user_input)
                user_action, done = offer_classifier.get_offer_and_arguments(
                    str(total_user_input)
                )
                if isinstance(user_action, Offer):
                    offer = ""
                    human_offer_dict = user_action.get_bid()
                    self.negotiation_gui.update_human_message(user_input)
                    self.negotiation_gui.update_offer("Your offer: " + offer)
                    human_offer = (
                        self.utility_space_controller.convert_offer_dict_to_list(
                            human_offer_dict
                        )
                    )
                    self.negotiation_gui.update_offer_utility(
                        str(
                            int(
                                self.human_utility_space.get_offer_utility(human_offer)
                                * 100
                            )
                        )
                    )
                    self.negotiation_gui.update_time(
                        round(self.time_controller.get_current_time(), 2) * 600
                    )
                    print("User Offer:", offer)
                self.previous_user_action = user_action

        if isinstance(user_action, Offer):
            self.negotiation_gui.update_offer_utility(
                str(int(self.human_utility_space.get_offer_utility(human_offer) * 100))
            )
            self.negotiation_gui.update_time(
                round(self.time_controller.get_current_time(), 2) * 600
            )
            self.negotiation_gui.update_status("Caduceus' turn.")
        else:
            self.negotiation_gui.update_status("Agreement is reached.")
            self.negotiation_gui.update_time(
                round(self.time_controller.get_current_time(), 2) * 600
            )
        self.previous_user_action = None
        self.human_sentences.append(total_user_input)
        return user_action 

    # def get_human_action(self):
    #     """
    #     Listen the user offer, then select keywords from sentence, check similarities and return what's left to the agent from user.
    #     """
    #     done = False
    #     offer_classifier = HolidayOfferClassifier(self.human_utility_space)
    #     self.negotiation_gui.update_human_message("-")
    #     self.negotiation_gui.update_time(
    #         round(self.time_controller.get_current_time(), 2) * 600
    #     )
    #     total_user_input = ""
    #     while not done:
    #         user_input = raw_input("Enter your offer: ")  # self.sentences[self.count]
    #         total_user_input += " " + user_input
    #         user_action, done = offer_classifier.get_offer_and_arguments(
    #             str(total_user_input)
    #         )
    #         if isinstance(user_action, Offer):
    #             offer = ""
    #             human_offer_dict = user_action.get_bid()
    #             self.negotiation_gui.update_human_message(user_input)
    #             self.negotiation_gui.update_offer("Your offer: " + offer)
    #             human_offer = self.utility_space_controller.convert_offer_dict_to_list(
    #                 human_offer_dict
    #             )
    #             self.negotiation_gui.update_offer_utility(
    #                 str(
    #                     int(
    #                         self.human_utility_space.get_offer_utility(human_offer)
    #                         * 100
    #                     )
    #                 )
    #             )
    #             self.negotiation_gui.update_time(
    #                 round(self.time_controller.get_current_time(), 2) * 600
    #             )
    #             print("User Offer:", offer)
    #     if isinstance(user_action, Offer):
    #         self.negotiation_gui.update_offer_utility(
    #             str(int(self.human_utility_space.get_offer_utility(human_offer) * 100))
    #         )
    #         self.negotiation_gui.update_time(
    #             round(self.time_controller.get_current_time(), 2) * 600
    #         )
    #         self.negotiation_gui.update_status("Caduceus' turn.")
    #     else:
    #         self.negotiation_gui.update_status("Agreement is reached.")
    #         self.negotiation_gui.update_time(
    #             round(self.time_controller.get_current_time(), 2) * 600
    #         )
    #     self.previous_user_action = None
    #     self.human_sentences.append(total_user_input)
    #     return user_action
