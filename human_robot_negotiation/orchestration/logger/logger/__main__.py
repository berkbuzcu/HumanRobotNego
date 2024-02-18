from . import *
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue

hant_logger = Logger()
queue_manager = MultiQueueHandler([HANTQueue.LOGGER])


while True:
    message = queue_manager.wait_for_message_from_queue(HANTQueue.LOGGER)

    if message.context == "session_init":
        '''
            participant_id
            agent_type
            interaction_type
            session_location
            domain
        '''
        hant_logger.create_session(**message.payload)

    elif message.context == "round":
        '''
            bidder
            offer
            agent_utility
            human_utility
            scaled_time
            move
            agent_mood
            predictions
            sentences
        '''
        hant_logger.log_round(**message.payload)

    elif message.context == "session_end":
        '''
            is_agreement
            final_scaled_time
            final_agent_score
            final_user_score
            total_offers
            human_awareness
            sensitivity_analysis
            robot_moods
        '''

        hant_logger.log_summary(**message.payload)
        break
