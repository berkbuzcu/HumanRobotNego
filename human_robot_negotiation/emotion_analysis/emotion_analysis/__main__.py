from .SessionManager.Session import Session
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue
from queuelib.message import CameraMessage, EmotionMessage

participant_name = "Berk"
session_number = "Session 1"
session_type = "FaceChannel"

queue_manager = MultiQueueHandler([HANTQueue.EMOTION])

queue_manager.send_message(prep_init_message("emotion_controller", HANTQueue.EMOTION))

config = queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

session_controller = Session(participant_name, session_number, session_type)

while True:
    msg = queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

    if msg.payload["action"] == "start_recording":
        # camera_controller.start()
        camera_message = CameraMessage("emotion_controller", {"action": "start_recording"}, "recording")
        queue_manager.send_message(camera_message)

        msg = queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

        if msg.payload["action"] == "stop_recording":
            stop_message = CameraMessage("emotion_controller", {"action": "stop_recording"}, "recording")
            faces_message = queue_manager.wait_for_message_from_queue(HANTQueue.CAMERA)
            faces = faces_message.payload["faces"]

            if session_controller:
                predictions, normalized_predictions = session_controller.stop(faces)
            else:
                predictions = {"Valance": 0.5, "Arousal": 0.5,
                               "Max_V": 0.5, "Min_V": 0.5, "Max_A": 0.5, "Min_A": 0.5}
                normalized_predictions = predictions

            queue_manager.send_message(EmotionMessage("emotion_controller", {
                "predictions": predictions,
                "normalized_predictions": normalized_predictions
            }, "emotion_output"))
