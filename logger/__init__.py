from logger.models import *
import os
import pathlib

PROJECT_DIR = pathlib.Path(__file__).parent
LOGS_DIR = PROJECT_DIR.parent / "logs"
DB_PATH = LOGS_DIR / "logs.sqlite3"


if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

if not os.path.exists(DB_PATH):
    create_tables()

class LoggerNew():
    def __init__(self, participant_uuid: str, agent_type: str, interaction_type: str, session_location: str, domain: str) -> None:
        self.session_id = SessionInformation.create(
            participant_uuid = participant_uuid,
            agent_type = agent_type,
            interaction_type = interaction_type,
            session_location = session_location,
            domain = domain
        )

    def log_round(self, bidder, offer, agent_utility, human_utility, scaled_time, move, agent_mood, predictions, sensitivity_class, sentences):        
        SessionOfferHistory.create(
            session_id=self.session_id,
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
            sensitivity_class=sensitivity_class,
            sentences=sentences,
        )
    
    def log_summary(self,
                    is_agreement,
                    final_scaled_time,
                    final_agent_score,
                    final_user_score,
                    total_offers,
                    human_awareness,
                    sensitivity_analysis,
                    robot_moods):
        SessionSummary.create(
            session_id=self.session_id,
            is_agreement= is_agreement,
            final_scaled_time= final_scaled_time,
            final_agent_score= final_agent_score,
            final_user_score= final_user_score,
            total_offers= total_offers,
            human_awareness= human_awareness,
            sensitivity_analysis= sensitivity_analysis,
            robot_moods= robot_moods
        )
        ...