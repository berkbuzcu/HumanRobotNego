from queuelib.enums import HANTQueue
from queuelib.message import HumanMessage
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from .speech_to_text_streaming_beta import SpeechStreamingRecognizerBeta

speech_controller = SpeechStreamingRecognizerBeta(domain_keywords=[])
queue_handler = MultiQueueHandler([HANTQueue.MICROPHONE], host="localhost")
queue_handler.send_message(prep_init_message("microphone", HANTQueue.MICROPHONE))

while True:
    print("Microphone: Waiting for message")
    msg = queue_handler.wait_for_message_from_queue(HANTQueue.MICROPHONE)

    if msg.payload["action"] == "get_recording":
        responses = speech_controller.listen_and_convert_to_text()

        response = {
            "responses": responses,
        }
        print("Responses: ", response)
        queue_handler.send_message(HumanMessage("human_controller", response, "microphone_result"))
