import numpy as np
import os

from capturing import Capturing
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue

camera_id = 0

# Load Camera Capturing
capturing = Capturing(camera_id)
queue_manager = MultiQueueHandler([HANTQueue.CAMERA])


def generate_round_folders(self):
    """
        Generates round folders.
    :return: None
    """
    faces_dir = os.path.join(self.round_dir % self.round, "faces/")
    faces_cut_dir = os.path.join(self.round_dir % self.round, "faces_cut/")
    imagined_dir = os.path.join(self.round_dir % self.round, "imagined/")
    frames_dir = os.path.join(self.round_dir % self.round, "frames/")

    os.mkdir(self.round_dir % self.round)
    os.mkdir(faces_dir)
    os.mkdir(faces_cut_dir)
    os.mkdir(imagined_dir)
    os.mkdir(frames_dir)


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

while True:
    message = queue_manager.wait_for_message_from_queue(HANTQueue.CAMERA)

    if message.payload["action"] == "start_recording":
        faces = []
        counter = 0
        while True:
            face = get_face(counter)
            counter += 1

            if face is None:
                continue

            faces.append(face)
