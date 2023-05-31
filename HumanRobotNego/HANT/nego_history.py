from HumanRobotNego.HANT.nego_action import Offer, Accept
from HumanRobotNego.HANT.sensitivity_calculator import SensitivityCalculator
import pandas as pd


class NegotiationHistory:
    def __init__(
        self, utility_space_controller, agent_utility_space, human_utility_space
    ):
        self.offer_history = []
        self.human_offer_history = []
        self.agent_offer_history = []
        self.utility_space_controller = utility_space_controller
        self.agent_utility_space = agent_utility_space
        self.human_utility_space = human_utility_space
        self.sensitivity_calculator = SensitivityCalculator()

    def add_to_history(self, bidder, offer, time, emotion, predictions):
        if bidder == "Agent":
            # Calculate utilities of both sides for agent offer.
            agent_utility = self.agent_utility_space.get_offer_utility(offer)
            human_utility = self.human_utility_space.get_offer_utility(offer)
            self.agent_offer_history.append(
                (bidder, offer, agent_utility, human_utility, time)
            )
        elif bidder == "Human":
            # Calculate utilities of both sides for human offer.
            agent_utility = self.agent_utility_space.get_offer_utility(offer)
            human_utility = self.human_utility_space.get_offer_utility(offer)
            self.human_offer_history.append(
                (bidder, offer, agent_utility, human_utility, time)
            )
        else:
            raise ("Invalid bidder.")
            
        self.offer_history.append(
            (
                bidder,
                offer,
                agent_utility,
                human_utility,
                time,
                emotion,
                predictions["Max_V"],
                predictions["Min_V"],
                predictions["Valance"],
                predictions["Max_V"],
                predictions["Min_V"],
                predictions["Arousal"],
             )
        )

    def get_agent_move_list(self):
        agent_history = list(zip(*self.agent_offer_history[:]))
        agent_moves = []
        if len(agent_history) > 0:
            agent_utilities = agent_history[2]
            human_utilities = agent_history[3]
            agent_moves = self.sensitivity_calculator.get_target_move_list(
                agent_utilities, human_utilities
            )
        return agent_moves

    def get_human_move_list(self):
        human_history = list(zip(*self.human_offer_history[:]))

        if len(human_history) < 2:
            print("Not enough offers to log (Human)!")
            return

        agent_utilities = human_history[2]
        human_utilities = human_history[3]
        human_moves = self.sensitivity_calculator.get_target_move_list(
            human_utilities, agent_utilities
        )
        return human_moves

    def extract_history_to_df(self):
        agent_moves = self.get_agent_move_list()
        human_moves = self.get_human_move_list()
        # Calculate human sensitivity rate and keep it for now.
        self.human_sensitivity_rates = self.sensitivity_calculator.get_sensitivity_rate(
            human_moves
        )
        # Create variable that will keep every offer in history as df.
        offer_df_list = []
        # Iterate every offer in the history.
        for offer_index, offer_hist in enumerate(self.offer_history):
            # If bidder is agent.
            if offer_hist[0] == "Agent":
                # Convert single offer to dataframe and add to list.
                d1 = {
                    "Bidder": offer_hist[0],
                    "Agent Utility": offer_hist[2],
                    "Human Utility": offer_hist[3],
                    "Offer": "Empty",
                    "Scaled Time": offer_hist[4],
                    "Move": agent_moves[offer_index // 2],
                    "Agent Emotion": offer_hist[5],
                    "Max V": offer_hist[6],
                    "Min V": offer_hist[7],
                    "Valance": offer_hist[8],
                    "Max A": offer_hist[9],
                    "Min A": offer_hist[10],
                    "Arousal": offer_hist[11],
                    "Sensitivity Class": "",
                }
                df1 = pd.DataFrame(data=d1, index=[offer_index])
                df1["Offer"] = df1["Offer"].astype(object)
                df1.at[offer_index, "Offer"] = offer_hist[1]
                offer_df_list.append(df1)
            # If bidder is human.
            else:
                sensitivity_prediction = ""
                
                if self.sensitivity_predictions != []:
                    sensitivity_prediction = self.sensitivity_predictions[offer_index // 2]

                d1 = {
                    "Bidder": offer_hist[0],
                    "Agent Utility": offer_hist[2],
                    "Human Utility": offer_hist[3],
                    "Offer": "Empty",
                    "Scaled Time": offer_hist[4],
                    "Move": human_moves[offer_index // 2],
                    "Agent Emotion": "",
                    "Max V": offer_hist[6],
                    "Min V": offer_hist[7],
                    "Valance": offer_hist[8],
                    "Max A": offer_hist[9],
                    "Min A": offer_hist[10],
                    "Arousal": offer_hist[11],
                    "Sensitivity Class": sensitivity_prediction,
                    "Sentences": self.sentences[offer_index // 2],
                }
                df1 = pd.DataFrame(data=d1, index=[offer_index])
                df1["Offer"] = df1["Offer"].astype(object)
                df1.at[offer_index, "Offer"] = offer_hist[1]
                offer_df_list.append(df1)
        # Return the list of offer history (df).
        return offer_df_list

    def get_last_offer(self):
        return self.offer_history[-1]

    def get_offer_count(self):
        return len(self.offer_history)

    def get_human_sensitivity_rates(self):
        return self.human_sensitivity_rates

    def get_human_awareness(self):
        agent_history = list(zip(*self.agent_offer_history[:]))
        human_history = list(zip(*self.human_offer_history[:]))
        if len(agent_history) > 0:
            agent_offer_agent_utilities = agent_history[2]
            agent_offer_human_utilities = agent_history[3]
            human_offer_agent_utilities = human_history[2]
            human_offer_human_utilities = human_history[3]

            return self.sensitivity_calculator.get_human_awareness(
                agent_offer_agent_utilities,
                agent_offer_human_utilities,
                human_offer_agent_utilities,
                human_offer_human_utilities,
            )
        else:
            return 0

    def set_sensitivity_predictions(self, sensitivity_predictions):
        self.sensitivity_predictions = sensitivity_predictions

    def set_sentences(self, sentences):
        self.sentences = sentences
