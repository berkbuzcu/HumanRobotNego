import time
import warnings

from corelib.nego_action import Accept
from queuelib.queue_manager import MultiQueueHandler
from .managers.agent_manager import AgentManager
from .managers.emotion_manager import EmotionManager
from .managers.gui_manager import GUIManager
from .managers.human_interaction_manager import HumanInteractionManager
from .managers.robot_manager import RobotManager
from .managers.logger_manager import LoggerManager
from .managers.time_manager import TimeManager
from .nego_timer import NegotiationTimer

warnings.simplefilter(action='ignore', category=FutureWarning)


def nego_over():
    # self.negotiation_gui.timer_widget.finish()
    # self.loading.show()
    print("NEGO IS OVER!!!")


class Core:
    def __init__(self, parameters):
        self.queue_handler = MultiQueueHandler()
        self.agent_utility_space = None
        self.human_utility_space = None

        self.running = False
        self.is_first_turn = True

        self.participant_name = parameters["participant_name"]
        self.session_number = parameters["session_type"].replace(" ", "_")
        self.session_type = parameters["facial_expression_model"]
        self.agent_preferences = parameters["agent_preferences"]
        self.human_preferences = parameters["human_preferences"]
        self.domain_info = parameters["domain_info"]
        self.deadline = parameters["deadline"]
        self.robot_name = parameters["robot_name"]

        print("CORE: Config applied: ", parameters)

        self.agent_manager = AgentManager()
        self.robot_manager = RobotManager()
        self.gui_manager = GUIManager()
        self.emotion_manager = EmotionManager()
        self.human_interaction_manager = HumanInteractionManager()
        self.logger_manager = LoggerManager()
        self.time_manager = TimeManager(self.deadline, self.timeout_negotiation)

    def end_negotiation(self, termination_type: str):
        agent_num_of_emotions = self.agent.receive_negotiation_over(self.participant_name, self.session_number,
                                                                    termination_type)
        self.robot_manager.send_nego_over(termination_type)

        if self.nego_history.get_offer_count() > 2:
            print("Enough bids to log")
            self.update_nego_history()
            human_awareness = self.nego_history.get_human_awareness()
            total_offers = self.nego_history.get_offer_count()
            human_sensitivity_dict = self.nego_history.get_human_sensitivity_rates()
            last_offer = self.nego_history.get_last_offer()

            time_passed, agent_score, user_score, agreement = (1, 0, 0, False) if termination_type == "timeout" else (
                last_offer[4], last_offer[2], last_offer[3], True)

            # LoggerNew.log_summary(
            #    robot_moods=agent_num_of_emotions,
            #    sensitivity_analysis=human_sensitivity_dict,
            #    human_awareness=human_awareness,
            #    total_offers=total_offers,
            #    final_scaled_time=time_passed,
            #    final_agent_score=agent_score,
            #    final_user_score=user_score,
            #    is_agreement=agreement)

        print("Logging complete")

    def timeout_negotiation(self):
        if self.running:
            self.running = False
            self.end_negotiation("timeout")

    def terminate_nego(self):
        if self.running:
            self.running = False

    def negotiate(self):
        self.robot_manager.send_start_negotiation()
        self.do_normal_nego()

    def send_agent_offer_to_human(self, agent_offer_to_human, mood):
        # Send the mood to robot
        if mood is not None:
            self.robot_manager.send_mood(mood)

        self.emotion_manager.start_camera()

        # send offer to robot interface and let it handle
        agent_sentence = self.robot_manager.send_offer(agent_offer_to_human)
        self.gui_manager.update_offer_message("Agent", agent_sentence)

    def do_normal_nego(self):
        while self.running:
            human_action = None
            start_time = -1
            if self.is_first_turn and start_time == -1:
                predictions = {"Valance": 0.0, "Arousal": 0.0,
                               "Max_V": 0.0, "Min_V": 0.0, "Max_A": 0.0, "Min_A": 0.0}
                normalized_predictions = predictions
                self.is_first_turn = False
            else:
                rem_time = time.time() - start_time
                if rem_time < 2.01:
                    print("Sleeping for: ", 2 - rem_time)
                    time.sleep(2 - rem_time)

                predictions, normalized_predictions = self.emotion_manager.stop_camera()

            self.gui_manager.update_status(f"{self.robot_name} is listening")

            while self.running:
                human_action, offer_done, total_user_input = self.human_interaction_manager.get_human_action()

                if isinstance(human_action, Accept):
                    self.end_negotiation("human")
                    return

                self.gui_manager.reset_offer_grid()
                self.gui_manager.update_offer_grid(human_action.get_bid("Human"), "blue")
                self.gui_manager.update_offer_message("Human", total_user_input)
                self.gui_manager.update_offer_utility("Human", str(int(self.human_utility_space.get_offer_utility(
                    human_action.get_bid("Human")) * 100)))

                if offer_done:
                    self.logger_manager.log_round(
                        bidder=human_action.get_bidder(),
                        offer=human_action,
                        scaled_time=self.time_manager.get_remaining_time(),
                        agent_mood="",
                        predictions=predictions,
                        agent_utility=self.agent_utility_space.get_offer_utility(human_action.get_bid("Agent")),
                        human_utility=self.human_utility_space.get_offer_utility(human_action.get_bid("Human")),
                        sentences=[],
                        move="offer",

                    )
                    break

            if not self.running:
                # self.end_negotiation("timeout")
                return

            self.gui_manager.update_offer_message(self.robot_name, "")
            self.gui_manager.update_status(f"{self.robot_name}'s turn")

            # Agent's generated offer for itself.
            self.agent_manager.send_offer(human_action, predictions, normalized_predictions)
            agent_action, agent_mood = self.agent_manager.receive_offer()

            # Check if agent accepts the offer.
            if isinstance(agent_action, Accept):
                self.end_negotiation("agent")
                return

            # Agent's offer to itself as list.
            agent_offer = agent_action.get_bid(perspective="Human")

            # Add agent offer to the logger list.
            # Send offer to the human.
            self.send_agent_offer_to_human(agent_offer, agent_mood)

            # Set negotiation gui according to agent's offer.
            self.gui_manager.update_offer_grid("Agent", agent_offer)

            self.logger_manager.log_round(
                bidder=agent_action.get_bidder(),
                offer=agent_action,
                scaled_time=self.time_manager.get_remaining_time(),
                agent_mood=agent_mood,
                predictions=predictions,
                agent_utility=self.agent_utility_space.get_offer_utility(agent_offer),
                human_utility=self.human_utility_space.get_offer_utility(human_action.get_bid("Human")),
                sentences=[],
                move="offer",
            )

            self.gui_manager.update_offer_utility(
                "Agent",
                str(
                    int(
                        self.human_utility_space.get_offer_utility(agent_offer) * 100
                    )
                )
            )
