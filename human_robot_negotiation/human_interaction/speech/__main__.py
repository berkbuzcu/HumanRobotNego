import json

import nltk
nltk.download('universal_tagset')
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue
from queuelib.message import HumanMessage, MicrophoneMessage
from .speech_controller import SpeechController

from corelib.offer_classifiers.holiday_offer_classifier import HolidayOfferClassifier
from corelib.offer_classifiers.offer_classifier import OfferClassifier
from corelib.utility_space import UtilitySpace
from corelib.nego_action import NormalActionFactory, ResourceAllocationActionFactory

queue_handler = MultiQueueHandler([HANTQueue.HUMAN, HANTQueue.MICROPHONE], correlation_id="human")
queue_handler.flush_queues()
#queue_handler.send_message(prep_init_message("human", HANTQueue.HUMAN))


speech_controller = None
module_name = "human_controller"

while True:
    print("Waiting message...")
    msg = queue_handler.wait_for_message_from_queue(HANTQueue.HUMAN)
    print("message: ", msg)

    if msg.context == "init":
        human_utility_space = UtilitySpace(msg.payload["human_preferences"])

        action_factory = NormalActionFactory(human_utility_space, bidder="Human")
        offer_classifier = HolidayOfferClassifier(human_utility_space, action_factory)
        if msg.payload["domain_info"]["domain_type"] == "resource_allocation":
            action_factory = ResourceAllocationActionFactory(human_utility_space, bidder="Human")
            offer_classifier = OfferClassifier(human_utility_space, action_factory)

        speech_controller = SpeechController(offer_classifier)

    elif msg.context == "human_offer":
        if msg.payload["action"] == "get_human_offer":
            microphone_message = MicrophoneMessage(module_name, {"action": "get_recording"})
            queue_handler.send_message(microphone_message)
            microphone_message = queue_handler.wait_for_message_from_queue(HANTQueue.MICROPHONE)
            if microphone_message.context == "microphone_result":
                user_action, offer_done, total_user_input = \
                    speech_controller.get_human_action(microphone_message.payload["responses"])
                response = {
                    "user_action": user_action.to_json_str(),
                    "offer_done": offer_done,
                    "total_user_input": total_user_input
                }
                print("RESP: ", response)
                queue_handler.send_message(HumanMessage(module_name, response))
