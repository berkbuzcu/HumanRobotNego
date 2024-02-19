import numpy as np
import time

from queuelib.enums import HANTQueue
from queuelib.queue_manager import MultiQueueHandler
from queuelib.message import CameraMessage
from .capturing import Capturing


# Load Camera Capturing
queue_manager = MultiQueueHandler([HANTQueue.CAMERA], host="localhost")


def get_face(id: int) -> np.ndarray:
    """
        Run Session's camera and return Face as Numpy Array
    :param id: Frame Index
    :return: Face Image
    """
    face = capturing.run(id)

    if face is None:
        return None

    return np.array(face, dtype=np.float32)


print("CAMERA INIT COMPLETE, WAITING INITIAL MESSAGE...")
init_message = queue_manager.wait_for_message_from_queue(HANTQueue.CAMERA)
init_payload = init_message.payload

camera_id = 0
user_id = init_payload["username"]
capturing = Capturing(user_id, camera_id)


while True:
    message = queue_manager.wait_for_message_from_queue(HANTQueue.CAMERA)

    _recording = False

    def stop_recording_callback(ch, method, properties, message):
        if message.payload["action"] == "stop_recording":
            global _recording
            _recording = False
            capturing.close()
            print("RECORD STOPPED...")


    if message.payload["action"] == "start_recording":
        print("RECORD STARTING...")

        counter = 0
        faces = []
        _recording = True

        queue_manager.non_blocking_message_from_queue(HANTQueue.CAMERA, stop_recording_callback)

        while _recording:
            face = get_face(counter)
            counter += 1

            if face is None:
                continue

            faces.append(face)

        message = CameraMessage("CAMERA", {"action": "stop_recording"}, "faces")
        queue_manager.send_message(message)
