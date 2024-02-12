import time
import warnings

from corelib.nego_action import Accept
from queuelib.queue_manager import MultiQueueHandler
from .managers.agent_manager import AgentManager
from .managers.emotion_manager import EmotionManager
from .managers.gui_manager import GUIManager
from .managers.human_interaction_manager import HumanInteractionManager
from .managers.robot_manager import RobotManager
from .nego_timer import NegotiationTimer

warnings.simplefilter(action='ignore', category=FutureWarning)


def nego_over():
    # self.negotiation_gui.timer_widget.finish()
    # self.loading.show()
    print("NEGO IS OVER!!!")


class Core():
    def __init__(self, parameters):
        super().__init__()
        self.queue_handler = MultiQueueHandler()
        self.agent_utility_space = None
        self.human_utility_space = None

        self.running = False
        self.is_first_turn = True

        self.participant_name = parameters["participant_name"]
        self.session_number = parameters["session_type"].replace(" ", "_")
        self.session_type = parameters["facial_expression_model"]
        self.human_interaction_type = parameters["input_type"]
        self.agent_interaction_type = parameters["output_type"]
        self.agent_type = parameters["agent_type"]
        self.agent_preferences = parameters["agent_preferences"]
        self.human_preferences = parameters["human_preferences"]
        self.robot_name = parameters["robot_name"]
        self.domain_info = parameters["domain_info"]
        self.deadline = parameters["deadline"]
        self.camera_id = parameters["camera_id"]

        # self.camera_controller = SessionCamera(self.participant_name, self.session_number, self.session_type,
        #                                       camera_id=self.camera_id)  # 30 seconds

        self.robot_manager = RobotManager()
        self.agent_manager = AgentManager()
        self.gui_manager = GUIManager()
        self.emotion_manager = EmotionManager()
        self.human_interaction_manager = HumanInteractionManager()

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

            #LoggerNew.log_summary(
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
            self.human_interaction_controller.recognizer.terminate_stream()

    def negotiate(self):
        self.robot_manager.send_start_negotiation()
        self.do_normal_nego()

    def generate_selected_tuples(self, offer):
        return [self.human_utility_space.get_value_coord(value) for value in offer.values()]

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

                predictions, normalized_predictions = self.emotion_manager.get_predictions()

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
                    # Add user offer to the history list.
                    # self.nego_history.add_to_history(
                    #    bidder=human_action.get_bidder(),
                    #    offer=human_action,
                    #    scaled_time=self.time_controller.get_remaining_time(),
                    #    agent_mood="",
                    #    predictions=predictions,
                    # )
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

            # self.nego_history.add_to_history(
            #     bidder=agent_action.get_bidder(),
            #     offer=agent_action,
            #     scaled_time=self.time_controller.get_remaining_time(),
            #     agent_mood=agent_mood,
            #     predictions=predictions,
            # )

            self.gui_manager.update_offer_utility(
                "Agent",
                str(
                    int(
                        self.human_utility_space.get_offer_utility(agent_offer) * 100
                    )
                )
            )
