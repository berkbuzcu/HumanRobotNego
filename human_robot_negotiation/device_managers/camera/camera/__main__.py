import numpy as np
import os

from .capturing import Capturing
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue

camera_id = "0"

# Load Camera Capturing
capturing = Capturing(camera_id)
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

while True:
    message = queue_manager.wait_for_message_from_queue(HANTQueue.CAMERA)

    if message.payload["action"] == "start_recording":
        faces = []
        counter = 0
        print("RECORD STARTING...")
        while True:
            face = get_face(counter)
            counter += 1

            if face is None:
                continue

            faces.append(face)

            message = queue_manager.get_message_from_queue(HANTQueue.CAMERA)

            if message is not None and message.payload["action"] == "stop_recording":
                print("RECORD STOPPING...")
                break
