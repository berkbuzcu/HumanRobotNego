from ..FaceChannel.FaceChannel.FaceChannelV1.imageProcessingUtil import imageProcessingUtil
import cv2
from PIL import Image as PILImage
from human_robot_negotiation.HANT.exceptions import CameraException


IMAGE_CUT_SIZE = (96, 96)

class Capturing:
    save_path_format: str
    save_cut_path_format: str
    save_frame_path_format: str
    camera_id: int
    face_model: imageProcessingUtil
    cap: cv2.VideoCapture

    def __init__(self, camera_id: int = 0):
        self.save_path_format = ""
        self.save_cut_path_format = ""
        self.save_frame_path_format = ""

        self.camera_id = camera_id

        self.face_model = imageProcessingUtil()

        self.cap = cv2.VideoCapture(self.camera_id)
    
        ret, frame = self.cap.read()

        if ret == False:
            raise CameraException()

    def run(self, id: int):
        """
        Get face from camera
        :param id: Image index
        :return: Face
        """
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id)

        ret, frame = self.cap.read()

        cv2.imwrite(self.save_frame_path_format % id, frame)

        dets, face = self.face_model.detectFace(frame)

        if face is None or face.size == 0:
            return None

        cv2.imwrite(self.save_path_format % id, face)

        return self.face_model.preProcess(face)

    def close(self):
        """
            Close the camera
        :return: None
        """
        if self.cap is not None:
            self.cap.release()

        self.cap = None
