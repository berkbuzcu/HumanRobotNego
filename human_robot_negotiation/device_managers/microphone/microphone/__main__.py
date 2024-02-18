from speech_to_text_streaming_beta import SpeechStreamingRecognizerBeta
from corelib.nego_action import Offer

from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import HumanMessage


speech_controller = SpeechStreamingRecognizerBeta(domain_keywords=[])
queue_handler = MultiQueueHandler([HANTQueue.MICROPHONE])

while True:
    msg = queue_handler.wait_for_message_from_queue(HANTQueue.MICROPHONE)

    if msg.payload["action"] == "get_recording":
        user_action, offer_done, total_user_input = speech_controller.get_human_action()

        response = {
            "user_action": user_action,
            "offer_done": offer_done,
            "total_user_input": total_user_input
        }

        queue_handler.send_message(HumanMessage("human_controller", response, True))

    elif msg.payload["action"] == "stop_recording":
        speech_controller.terminate_stream()
        break
