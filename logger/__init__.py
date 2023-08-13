from logger.models import *
import os
import pathlib
import typing as t

if not os.path.exists(DB_FOLDER_PATH):
    os.mkdir(DB_FOLDER_PATH)

if not os.path.exists(DB_PATH):
    create_tables()

class LoggerNew():
    session_id = 0

    @classmethod
    def log_solver(cls, log_items: t.Dict[str, t.Any]):
        log_items["session_id"] = cls.session_id
        SolverAgentLogs.create(**log_items)

    @classmethod
    def log_hybrid(cls, log_items):
        log_items["session_id"] = cls.session_id
        HybridAgentLogs.create(**log_items)

    @classmethod
    def create_session(cls, participant_uuid: str, agent_type: str, interaction_type: str, session_location: str, domain: str) -> None:
        cls.session_id = SessionInformation.create(
            participant_uuid = participant_uuid,
            agent_type = agent_type,
            interaction_type = interaction_type,
            session_location = session_location,
            domain = domain
        )

    @classmethod
    def log_round(cls, bidder, offer, agent_utility, human_utility, scaled_time, move, agent_mood, predictions, sentences):        
        SessionOfferHistory.create(
            session_id=cls.session_id,
            bidder=bidder,
            agent_utility=agent_utility,
            human_utility=human_utility,
            offer=offer,
            scaled_time=scaled_time,
            move=move,
            agent_mood=agent_mood,
            max_valance= predictions["Max_V"],
            min_valance= predictions["Min_V"],
            valance= predictions["Valance"],
            max_arousal= predictions["Max_V"],
            min_arousal= predictions["Min_V"],
            arousal= predictions["Arousal"],
            sentences=sentences,
        )
    
    @classmethod
    def log_summary(cls,
                    is_agreement,
                    final_scaled_time,
                    final_agent_score,
                    final_user_score,
                    total_offers,
                    human_awareness,
                    sensitivity_analysis,
                    robot_moods):
        SessionSummary.create(
            session_id=cls.session_id,
            is_agreement= is_agreement,
            final_scaled_time= final_scaled_time,
            final_agent_score= final_agent_score,
            final_user_score= final_user_score,
            total_offers= total_offers,
            human_awareness= human_awareness,
            sensitivity_analysis= sensitivity_analysis,
            robot_moods= robot_moods
        )