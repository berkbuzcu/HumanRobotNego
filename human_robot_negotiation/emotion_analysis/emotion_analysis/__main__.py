from .SessionManager.Session import SessionCamera
from queuelib.queue_manager import MultiQueueHandler, prep_init_message
from queuelib.enums import HANTQueue

participant_name = "Berk"
session_number = "Session 1"
session_type = "FaceChannel"

queue_manager = MultiQueueHandler([HANTQueue.EMOTION.value])

queue_manager.send_message(prep_init_message("emotion_controller", HANTQueue.EMOTION))

config = queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

camera_controller = SessionCamera(participant_name, session_number, session_type, camera_id=0)

while True:
    msg = queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

    if msg["action"] == "start_recording":
        camera_controller.start()

        msg = queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

        if msg["action"] == "stop_recording":
            if camera_controller:
                predictions, normalized_predictions = camera_controller.stop()
            else:
                predictions = {"Valance": 0.5, "Arousal": 0.5,
                               "Max_V": 0.5, "Min_V": 0.5, "Max_A": 0.5, "Min_A": 0.5}
                normalized_predictions = predictions
            queue_manager.send_message(HANTQueue.EMOTION.value, {
                "predictions": predictions,
                "normalized_predictions": normalized_predictions
            })
