import json

from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue
from queuelib.message import HumanMessage, MicrophoneMessage
from speech_controller import SpeechController

from corelib.offer_classifiers.holiday_offer_classifier import HolidayOfferClassifier
from corelib.offer_classifiers.offer_classifier import OfferClassifier

queue_handler = MultiQueueHandler(HANTQueue.HUMAN, HANTQueue.MICROPHONE)
queue_handler.send_message(prep_init_message("human", HANTQueue.HUMAN))

domain_message = queue_handler.wait_for_message_from_queue(HANTQueue.HUMAN)

offer_classifier = HolidayOfferClassifier
if domain_message.payload["domain_info"]["type"] == "resource_allocation":
    offer_classifier = OfferClassifier

speech_controller = SpeechController(offer_classifier)

module_name = "human_controller"

while True:
    msg = queue_handler.wait_for_message_from_queue(HANTQueue.HUMAN)

    if msg.payload["action"] == "get_human_offer":
        microphone_message = MicrophoneMessage(module_name, {"action": "get_recording"})
        queue_handler.send_message(microphone_message)

        microphone_message = queue_handler.wait_for_message_from_queue(HANTQueue.MICROPHONE)
        user_action, offer_done, total_user_input = \
            speech_controller.get_human_action(microphone_message.payload["user_input"])

        response = {
            "user_action": user_action,
            "offer_done": offer_done,
            "total_user_input": total_user_input
        }

        queue_handler.send_message(HumanMessage(module_name, response))
