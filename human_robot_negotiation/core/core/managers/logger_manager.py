from queuelib.queue_manager import MultiQueueHandler
from queuelib.message import LoggerMessage
from .abstract_manager import AbstractManager


class LoggerManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def log_session_init(self, participant_id, agent_type, interaction_type, session_location, domain):
        message_context = "session_init"
        message_payload = {
            "participant_id": participant_id,
            "agent_type": agent_type,
            "interaction_type": interaction_type,
            "session_location": session_location,
            "domain": domain,
        }

        message = LoggerMessage("CORE", message_payload, message_context)
        self.queue_handler.send_message(message)

    def log_round(self, bidder, offer, agent_utility, human_utility,
                  scaled_time, move, agent_mood, predictions, sentences):
        message_context = "round"
        message_payload = {
            "bidder": bidder,
            "offer": offer,
            "agent_utility": agent_utility,
            "human_utility": human_utility,
            "scaled_time": scaled_time,
            "move": move,
            "agent_mood": agent_mood,
            "predictions": predictions,
            "sentences": sentences,
        }

        message = LoggerMessage("CORE", message_payload, message_context)
        self.queue_handler.send_message(message)

    def log_session_end(self, is_agreement, final_scaled_time, final_agent_score, final_user_score, total_offers,
                        human_awareness, sensitivity_analysis, robot_moods):
        message_context = "session_end"
        message_payload = {
            "is_agreement": is_agreement,
            "final_scaled_time": final_scaled_time,
            "final_agent_score": final_agent_score,
            "final_user_score": final_user_score,
            "total_offers": total_offers,
            "human_awareness": human_awareness,
            "sensitivity_analysis": sensitivity_analysis,
            "robot_moods": robot_moods,
        }

        message = LoggerMessage("CORE", message_payload, message_context)
        self.queue_handler.send_message(message)
