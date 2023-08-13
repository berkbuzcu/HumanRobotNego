import time
import warnings

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThreadPool, QObject, Signal

from human_robot_negotiation import DOMAINS_DIR
from human_robot_negotiation import PROJECT_DIR
from human_robot_negotiation.HANT import nego_action
from human_robot_negotiation.HANT.nego_history import NegotiationHistory
from human_robot_negotiation.HANT.utility_space import UtilitySpace
from human_robot_negotiation.HANT.utility_space_controller import UtilitySpaceController

from human_robot_negotiation.HANT.nego_timer import NegotiationTimer
from human_robot_negotiation.HANT.nego_worker import NegotiationWorker
from human_robot_negotiation.HANT.robot_manager import RobotManager

from human_robot_negotiation.human_interaction_models.holiday_offer_classifier import HolidayOfferClassifier
from human_robot_negotiation.human_interaction_models.offer_classifier import OfferClassifier

from human_robot_negotiation.agent.solver_agent.solver_agent import SolverAgent
from human_robot_negotiation.agent.hybrid_agent import HybridAgent
from human_robot_negotiation.agent.demo_hybrid_agent import DemoHybridAgent
from human_robot_negotiation.agent.abstract_agent import AbstractAgent

from human_robot_negotiation.human_interaction_models.speech_controller import SpeechController
#from human_robot_negotiation.human_interaction_models.human_cli import HumanCLI

from human_robot_negotiation.gui.nego_gui import NegotiationGUI
from human_robot_negotiation.EmotionCapturing.SessionManager.Session import SessionCamera

from human_robot_negotiation.gui.config_manager import ConfigManager

from logger import LoggerNew


warnings.simplefilter(action='ignore', category=FutureWarning)

class HANTSignals(QObject):
    nego_over = Signal()
    

class HANT(QApplication):
    config_manager: ConfigManager
    robot_manager: RobotManager
    threadpool: QThreadPool
    agent: AbstractAgent

    def __init__(self):
        super().__init__()

        self.config_manager = ConfigManager(self)
        self.config_manager.show()
        self.robot_manager = RobotManager()
        self.threadpool = QThreadPool()

    def negotiation_setup(
        self,
        parameters
    ):
        participant_name=parameters["Participant Name"]
        session_number=parameters["Session Type"]
        session_type=parameters["Facial Expression Model"]
        human_interaction_type=parameters["Input Type"]
        agent_interaction_type=parameters["Output Type"]
        agent_type=parameters["Agent Type"]
        agent_preference_file=parameters["agent-domain"]
        human_preference_file=parameters["human-domain"]
        robot_name=parameters["Robot Name"]
        domain_name=parameters["Domain"]
        deadline=parameters["Deadline"]
        self.camera_id=parameters["Camera ID"]

        self.robot_name = robot_name
        self.time_controller = NegotiationTimer(deadline * 10**3, self.timeout_negotiation)
        
        self.camera_controller = SessionCamera(participant_name, session_number, session_type, camera_id=self.camera_id) # 30 seconds


        self.negotiation_gui = NegotiationGUI(self.screens()[-1], self.time_controller, self.robot_name)
        self.negotiation_worker = NegotiationWorker(self)

        print(participant_name, session_number, session_type, self.camera_id, "Deadline: ", deadline)

        domain_file = str(DOMAINS_DIR / domain_name / f"{domain_name}.xml")
        self.set_utility_space(
            agent_preference_file, human_preference_file, domain_file
        )

        self.is_first_turn = True
        self.running = True

        self.participant_name: str = participant_name
        self.session_number: str = session_number.replace(" ", "_") # Session 1
        self.session_type: str = session_type
        
        #name, session_type (demo, 1, 2), "face_channel" | "cl"

        self.set_agent_type(agent_type)
        self.robot_manager.start_robot_server(agent_interaction_type)
        
        self.time_controller.start_signal.emit()
        self.set_human_interaction_type(human_interaction_type, domain_file)
        
        self.grid = self.human_utility_space.get_2d_ranked_grid_colored()
        self.negotiation_gui.create_table([issue.title() for issue in self.human_utility_space.issue_names], self.grid)
        self.negotiation_gui.showFullScreen()

        print("CAMERA ID: ", self.camera_id, "(MAKE SURE ITS 1)")
        print("SESSION: ", self.session_number)
        print("SESSION TYPE: ", self.session_type)
        print("DOMAIN: ", domain_name, " AGENT: ", agent_preference_file, " HUMAN: ", human_preference_file)
        print("AGENT TYPE:", agent_type, " : ", agent_interaction_type)

        LoggerNew.create_session(participant_name, agent_type, agent_interaction_type, "SBU", domain_name)

        self.threadpool.start(self.negotiation_worker)

    def nego_over(self):
        #self.negotiation_gui.timer_widget.finish()
        #self.loading.show()
        print("NEGO IS OVER!!!")

    def set_human_interaction_type(self, human_interaction_type, domain_file):
        if human_interaction_type == "Speech":
            self.human_interaction_controller = SpeechController(
                self.offer_classifier
            )
        # elif human_interaction_type == "Human-CLI":
        #    self.human_interaction_controller = HumanCLI(
        #        self.human_utility_space,
        #        domain_file,
        #        self.negotiation_gui,
        #        self.time_controller,
        #    )
        else:
            raise Exception("Invalid human interaction type.")

    def set_utility_space(
        self, agent_preference_file, human_preference_file, domain_file
    ):
        self.utility_space_controller = UtilitySpaceController(domain_file)
        self.agent_utility_space = UtilitySpace(agent_preference_file)
        self.human_utility_space = UtilitySpace(human_preference_file)

        action_factory_selector = {
            "Resource Allocation": nego_action.ResourceAllocationActionFactory,
            "Normal": nego_action.NormalActionFactory,
        }

        offer_classifier_selector = {
            "Resource Allocation": OfferClassifier,
            "Normal": HolidayOfferClassifier
        }

        self.human_action_factory = action_factory_selector[self.utility_space_controller.domain_type](
            self.human_utility_space, "Human")
        self.agent_action_factory = action_factory_selector[self.utility_space_controller.domain_type](
            self.agent_utility_space, "Agent")

        self.offer_classifier = offer_classifier_selector[self.utility_space_controller.domain_type](
            self.human_utility_space, self.human_action_factory)

        self.nego_history = NegotiationHistory(
            self.utility_space_controller,
            self.agent_utility_space,
            self.human_utility_space,
        )

    def set_agent_type(self, agent_type):
        if agent_type == "Solver":
            self.agent = SolverAgent(self.agent_utility_space,
                                self.time_controller, self.agent_action_factory)
        elif agent_type == "Hybrid":
            self.agent = HybridAgent(self.agent_utility_space,
                                self.time_controller, self.agent_action_factory)
        elif agent_type == "DemoHybrid":
            self.agent = DemoHybridAgent(self.agent_utility_space,
                                self.time_controller, self.agent_action_factory)
        else:
            raise Exception("Invalid agent type.")


    def update_grid_by_offer(self, offer, color):
        changed_items = []
        for issue, value in offer.items():
            coords = self.human_utility_space.get_value_coord(f"{issue}_{value}")
            changed_items.append((coords[0], coords[1], value, color))
        self.negotiation_gui.update_grid_by_offer(changed_items)

    def send_agent_offer_to_human(self, agent_offer_to_human, mood):
        # Send the mood to robot
        if mood != None:
            self.robot_manager.send_mood(mood)

        if self.camera_controller:
            self.camera_controller.start()
            
        # send offer to robot interface and let it handle
        agent_sentence = self.robot_manager.send_bid(agent_offer_to_human)
        self.negotiation_gui.update_agent_message(agent_sentence)

    def update_nego_history(self):
        self.nego_history.set_sentences(self.human_interaction_controller.human_sentences)

    def end_negotiation(self, termination_type: str):
        agent_num_of_emotions = self.agent.receive_negotiation_over(self.participant_name, self.session_number, termination_type)
        self.robot_manager.send_nego_over(termination_type)
        
        if self.nego_history.get_offer_count() > 2:
            print("Enough bids to log")            
            self.update_nego_history()
            human_awareness = self.nego_history.get_human_awareness()
            total_offers = self.nego_history.get_offer_count()
            human_sensitivity_dict = self.nego_history.get_human_sensitivity_rates()
            last_offer = self.nego_history.get_last_offer()

            time_passed, agent_score, user_score, agreement = (1, 0, 0, False) if termination_type == "timeout" else (last_offer[4], last_offer[2], last_offer[3], True)


            LoggerNew.log_summary(
                robot_moods=agent_num_of_emotions,
                sensitivity_analysis=human_sensitivity_dict,
                human_awareness=human_awareness,
                total_offers=total_offers,
                final_scaled_time=time_passed,
                final_agent_score=agent_score,
                final_user_score=user_score,
                is_agreement=agreement)
        
        print("Logging complete")
        self.time_controller.finish_signal.emit()
        self.config_manager.reset_manager()
        self.negotiation_gui.clean_gui.emit()
        self.camera_controller.close()

    def timeout_negotiation(self):
        if self.running:
            self.running = False
            self.human_interaction_controller.recognizer.terminate_stream()
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

                if self.camera_controller:
                    predictions, normalized_predictions = self.camera_controller.stop()
                else:
                    predictions = {"Valance": 0.5, "Arousal": 0.5,
                                   "Max_V": 0.5, "Min_V": 0.5, "Max_A": 0.5, "Min_A": 0.5}
                    normalized_predictions = predictions               
            
            print("PREDS: ", predictions)
    
            self.negotiation_gui.update_status(f"{self.robot_name} is listening")
            
            while self.running:
                (human_action, offer_done, total_user_input) = self.human_interaction_controller.get_human_action()
                
                received_time = self.time_controller.get_remaining_time()
                print(received_time)
                if isinstance(human_action, nego_action.Accept):
                    self.end_negotiation("human")
                    return

                self.negotiation_gui.reset_board()

                self.update_grid_by_offer(human_action.get_bid("Human"), "blue")
                self.negotiation_gui.update_human_message(total_user_input)
                self.negotiation_gui.update_offer_utility(
                    str(int(self.human_utility_space.get_offer_utility(human_action.get_bid("Human")) * 100)))

                print("HUMAN OFFER UTILITY: ", str(int(self.human_utility_space.get_offer_utility(human_action.get_bid("Human")) * 100)))

                if offer_done:
                    # Add user offer to the history list.
                    self.nego_history.add_to_history(
                        bidder=human_action.get_bidder(),
                        offer=human_action,
                        scaled_time=self.time_controller.get_remaining_time(),
                        agent_mood="",
                        predictions=predictions,
                    )
                    break

            if not self.running:
                #self.end_negotiation("timeout")
                return

            self.negotiation_gui.update_agent_message("")
            self.negotiation_gui.update_status(f"{self.robot_name}'s turn")
            
            # Agent's generated offer for itself.
            (
                agent_action,
                agent_mood,
            ) = self.agent.receive_offer(human_action, predictions, normalized_predictions)
            # Check if agent accepts the offer.
            if isinstance(agent_action, nego_action.Accept):
                self.end_negotiation("agent")
                return

            # Agent's offer to itself as list.
            agent_offer = agent_action.get_bid(perspective="Human")

            # Add agent offer to the logger list.
            # Send offer to the human.
            start_time = time.time()
            self.send_agent_offer_to_human(agent_offer, agent_mood)
            
            # Set negotiation gui according to agent's offer.
            self.update_grid_by_offer(agent_offer, "red")

            self.nego_history.add_to_history(
                bidder=agent_action.get_bidder(),
                offer=agent_action,
                scaled_time=self.time_controller.get_remaining_time(),
                agent_mood=agent_mood,
                predictions=predictions,
            )

            self.negotiation_gui.update_offer_utility(
                str(
                    int(
                        self.human_utility_space.get_offer_utility(agent_offer) * 100
                    )
                )
            )