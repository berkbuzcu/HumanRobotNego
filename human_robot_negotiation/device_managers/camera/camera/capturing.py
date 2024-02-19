import cv2
import os
from .utils import imageProcessingUtil
from . import IMAGE_PATH

IMAGE_CUT_SIZE = (96, 96)


class CameraException(Exception):
    def __init__(self):
        super().__init__()


class Capturing:
    user_path: str
    round: int
    camera_id: int
    face_model: imageProcessingUtil
    cap: cv2.VideoCapture

    def __init__(self, user_id: str, camera_id: int = 0):
        self.round = 0
        self.user_id = user_id

        self.camera_id = camera_id
        self.face_model = imageProcessingUtil()
        self.cap = cv2.VideoCapture(self.camera_id)

        ret, frame = self.cap.read()

        if ret == False:
            raise CameraException()


    def create_user_dir(self, round):
        user_dir = IMAGE_PATH / self.user_id
        round_dir = user_dir / str(round)
        self.faces_dir = round_dir / "faces"
        self.faces_cut_dir = round_dir / "faces_cut"
        self.imagined_dir = round_dir / "imagined"
        self.frames_dir = round_dir / "frames"

        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
        if not os.path.exists(round_dir):
            os.mkdir(round_dir)
            os.mkdir(self.faces_dir)
            os.mkdir(self.faces_cut_dir)
            os.mkdir(self.imagined_dir)
            os.mkdir(self.frames_dir)

    def run(self, id: int):
        """
        Get face from camera
        :param id: Image index
        :return: Face
        """
        self.create_user_dir(self.round)

        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id)

        ret, frame = self.cap.read()

        cv2.imwrite(str((self.frames_dir / (str(id) + ".jpg")).absolute()), frame)

        dets, face = self.face_model.detectFace(frame)

        if face is None or face.size == 0:
            return None

        cv2.imwrite(str((self.faces_dir / (str(id) + ".jpg")).absolute()), face)

        return self.face_model.preProcess(face)

    def close(self):
        """
            Close the camera
        :return: None
        """
        if self.cap is not None:
            self.cap.release()

        self.cap = None
        self.round += 1
