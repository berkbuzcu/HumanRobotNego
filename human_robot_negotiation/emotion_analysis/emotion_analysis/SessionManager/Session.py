import copy
import typing as t

from .AbstractSession import *
from .Capturing import Capturing


class SessionCamera():
    capturing: Capturing
    _capturing: bool
    thread_capturing: Thread
    camera_id: int

    def __init__(self, participant_name: str, session_id: str, session_type: str, camera_id: int = 0):
        """
            Constructor
        :param session_name: Session Name for Logging
        :param use_face_channel: Prediction will be done with FaceChannel, or CL Model
        :param camera_id: Camera ID for recording
        """
        self.camera_id = camera_id

        # Load Camera Capturing
        self.capturing = Capturing(camera_id)

        self._capturing = False
        self.thread_capturing = None

        super(SessionCamera, self).__init__(participant_name, session_id, session_type)



    def get_valid_faces(self, predictions: list) -> list:
        # Get Stats of the FaceChannel prediction of the current round
        mean_arousal = float(np.mean(predictions[0]))
        std_arousal = float(np.std(predictions[0]))

        mean_valance = float(np.mean(predictions[1]))
        std_valance = float(np.std(predictions[1]))

        valid_faces = []
        for i in range(len(predictions[0])):
            # If the arousal and valance of that image is close to mean, ignore it.
            if mean_arousal - std_arousal <= predictions[0][i][
                0] <= mean_arousal + std_arousal and mean_valance - std_valance <= predictions[1][i][
                0] <= mean_valance + std_valance:
                continue

            # Add the path of corresponding image
            valid_faces.append(self.capturing.save_path_format % i)

        # The models cannot work if the number of images is less than 2
        while len(valid_faces) < 2:
            valid_faces.append(self.capturing.save_path_format % 0)

        return valid_faces

    def stop(self) -> t.Tuple[t.Dict[str, float], t.Dict[str, float]]:
        """
            Stop Recording thread. Also, it runs FaceChannel and CL Model.
        :return: Prediction of the model
        """

