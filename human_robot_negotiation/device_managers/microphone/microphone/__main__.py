from queuelib.enums import HANTQueue
from queuelib.message import MicrophoneMessage
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from .speech_to_text_streaming_beta import SpeechStreamingRecognizerBeta
import time

queue_handler = MultiQueueHandler([HANTQueue.MICROPHONE], host="localhost", correlation_id="microphone")
#queue_handler.send_message(prep_init_message("microphone", HANTQueue.MICROPHONE))
queue_handler.flush_queues()
speech_controller = SpeechStreamingRecognizerBeta(domain_keywords=[])

while True:
    print("Microphone: Waiting for message")
    time.sleep(0.5)
    msg = queue_handler.wait_for_message_from_queue(HANTQueue.MICROPHONE)

    if msg.payload["action"] == "get_recording":
        responses = speech_controller.listen_and_convert_to_text()

        response = {
            "responses": responses,
        }
        print("Responses: ", response)
        queue_handler.send_message(MicrophoneMessage("microphone", response, "microphone_result"))
