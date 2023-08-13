from human_robot_negotiation.HANT.nego_action import Offer
import typing as t

class MoodController:
    def __init__(self, utility_space, time_controller):
        # Set utility space.
        self.utility_space = utility_space
        # Set time controller.
        self.time_controller = time_controller
        # Keep human's previous offers to compare with current offer.
        self.opponent_previous_offers = []
        # Human's previous offer utility.
        self.opponent_previous_offer_utility = None
        # First warning flag for deadline.
        self.did_first_warn = False
        # Second warning flag for deadline.
        self.did_second_warn = False
        # Third warning flag for deadline.
        self.did_third_warn = False

        self.num_of_moods = {
            None: 0,
            "Frustrated": 0,
            "Annoyed": 0,
            "Dissatisfied": 0,
            "Neutral": 0,
            "Convinced": 0,
            "Content": 0,
            "Worried": 0,
        }

    def get_mood(self, human_offer: t.Dict[str, str]) -> str:
        """
        This function gets offer of the opponent's and lower threshold of the current tactic as input.
        Return robot mood and mood method to call and updates mood counts.
        """
        # Set default mood and mood file to none.
        mood = None

        # If 6 minutes remaining.
        if self.time_controller.get_current_time() > 0.6 and not self.did_first_warn:
            self.did_first_warn = True
            mood = "Worried"
        # If 4 minutes remaining.
        elif (
            self.time_controller.get_current_time() > 0.73 and not self.did_second_warn
        ):
            self.did_second_warn = True
            mood = "Worried"
        # If 2 minutes remaining.
        elif self.time_controller.get_current_time() > 0.86 and not self.did_third_warn:
            self.did_third_warn = True
            mood = "Worried"
        # If offer utility below reservation value or time is too close and utility is below 0.5
        elif (self.utility_space.get_offer_utility(human_offer) < 0.4) or (self.utility_space.get_offer_utility(human_offer) < 0.5 and self.time_controller.get_current_time() > 0.73):
            mood = "Frustrated"
        # Check whether we have previous utility or not, so that we can compare with previous offers & utilities.
        elif not self.opponent_previous_offer_utility == None:
            # Calculate the utility diff between this and previous offer.
            utility_delta = (
                self.utility_space.get_offer_utility(human_offer) - self.opponent_previous_offer_utility
            )

            if (
                len(self.opponent_previous_offers) >= 2 and human_offer == self.opponent_previous_offers[-1] and human_offer == self.opponent_previous_offers[-2]
            ):
                mood = "Frustrated"
            elif human_offer == self.opponent_previous_offers[-1]:
                mood = "Annoyed"
            elif utility_delta == 0:
                mood = "Neutral"
            elif 0 < utility_delta and utility_delta <= 0.25:
                mood = "Convinced"
            elif 0.25 < utility_delta:
                mood = "Content"
            elif -0.25 <= utility_delta < 0:
                mood = "Dissatisfied"
            elif utility_delta < -0.25:
                mood = "Annoyed"

        # Set offer's utility as previous after done.
        self.opponent_previous_offer_utility = self.utility_space.get_offer_utility(
            human_offer
        )
        # Append to the offer history.
        self.opponent_previous_offers.append(human_offer)
        # Return the robot action.

        self.num_of_moods[mood] += 1

        return mood

    def get_num_of_moods(self):
        return self.num_of_moods
