import json

from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue
from speech_controller import SpeechController

from corelib.offer_classifiers.holiday_offer_classifier import HolidayOfferClassifier
from corelib.offer_classifiers.offer_classifier import OfferClassifier

queue_handler = MultiQueueHandler(HANTQueue.HUMAN.value)
queue_handler.send_message(HANTQueue.HUMAN.value, prep_init_message("human"))

msg = queue_handler.wait_for_message_from_queue(HANTQueue.HUMAN.value)

offer_classifier = HolidayOfferClassifier
if msg["domain_info"]["type"] == "resource_allocation":
    offer_classifier = OfferClassifier

speech_controller = SpeechController(offer_classifier)

while True:
    msg = queue_handler.wait_for_message_from_queue(HANTQueue.HUMAN.value)

    if msg["action"] == "get_recording":
        user_action, offer_done, total_user_input = speech_controller.get_human_action()

        queue_handler.send_message(HANTQueue.HUMAN.value, json.dumps({"user_action": user_action,
                                                                      "offer_done": offer_done,
                                                                      "total_user_input": total_user_input}))
