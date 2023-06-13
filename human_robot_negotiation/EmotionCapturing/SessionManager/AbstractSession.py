import json
import os
import shutil
import time
import copy
import pandas as pd
import numpy as np
import tensorflow as tf

from threading import Thread
from human_robot_negotiation.EmotionCapturing.FaceChannel.FaceChannel.FaceChannelV1.FaceChannelV1 import FaceChannelV1
from abc import ABC, abstractmethod
from human_robot_negotiation import PROJECT_DIR

SESSIONS_DIR = str(PROJECT_DIR.parent / "sessions")
SAVED_GWRS_DIR = str(PROJECT_DIR / "EmotionCapturing" / "saved_gwrs")

# Global Tensorflow Graph and Session for multi-thread operations.
global graph
graph = tf.compat.v1.get_default_graph()
global sess
# sess = tf.compat.v1.Session(graph=graph, config=tf.compat.v1.ConfigProto(allow_soft_placement=True))
sess = tf.compat.v1.InteractiveSession(graph=graph)

class AbstractSession(ABC):
    session_name: str
    participant_name: str
    session_id: str
    round: int
    log_dir: str
    round_dir: str
    gwr_dir: str
    log_face_channel: pd.DataFrame
    log_face_channel_path: str
    log_cl: pd.DataFrame
    log_cl_path: str
    face_channel: FaceChannelV1
    session_type: str
    train_cl: bool
    _faces: list
    thread_capturing: Thread
    max_a: float
    min_a: float
    max_v: float
    min_v: float

    def __init__(self, participant_name: str, session_id: str, session_type: str):
        """
            Constructor
            :param participant_name: Unique participant name
            :session_id: 'Demo' or 'Session x'
            :session_type: 'face_channel_only', 'face_channel', 'continual_learning', 'seven_emotion'
        """

        self.participant_name = participant_name
        self.session_id = session_id
        self.session_name = f"{participant_name}_{session_id}"
        self.session_type = session_type
        self.round = 0
        
        self.train_cl = session_type == "continual_learning" or session_id == "Demo"

        if self.train_cl:
            from ..FaceChannel.CLModel.cl_model_c3_faster import predict

            self.prediction_from_cl = predict

        if not os.path.isdir(SESSIONS_DIR):
            os.mkdir(SESSIONS_DIR)

        if not os.path.isdir(SAVED_GWRS_DIR):
            os.mkdir(SAVED_GWRS_DIR)

        experiment_gwrs = os.path.join(SAVED_GWRS_DIR, f"exp_{participant_name}/")
        arousal_valance_logs = os.path.join(SESSIONS_DIR, f"arousal_valance/")

        if not os.path.isdir(arousal_valance_logs):
            os.mkdir(arousal_valance_logs)

        if not os.path.isdir(experiment_gwrs):
            os.mkdir(experiment_gwrs)

        if session_id == "Demo":
            self.max_a = -1.
            self.max_v = -1.
            self.min_a = 1.
            self.min_v = 1.
        elif os.path.exists(os.path.join(SESSIONS_DIR, f"arousal_valance/") + self.participant_name + ".json"):
            with open(os.path.join(SESSIONS_DIR, f"arousal_valance/") + self.participant_name + ".json", "r") as f:
                arousal_valance_log = json.load(f)

                self.max_a = arousal_valance_log["max_a"]
                self.min_a = arousal_valance_log["min_a"]
                self.max_v = arousal_valance_log["max_v"]
                self.min_v = arousal_valance_log["min_v"]

        # Generate Paths
        self.log_dir = os.path.join(SESSIONS_DIR, self.session_name + "/")
        self.round_dir = os.path.join(self.log_dir, "round_%d/")

        self.gwr_dir = os.path.join(SAVED_GWRS_DIR, "exp_%s/" % participant_name)

        # Generate Logger
        self.log_face_channel_path = os.path.join(self.log_dir, "face_channel.csv")
        self.log_face_channel = pd.DataFrame(columns=["Round", "Arousal", "Valance", "Max_A", "Min_A", "Max_V", "Min_V"])

        self.log_cl_path = os.path.join(self.log_dir, "cl.csv")
        self.log_cl = pd.DataFrame(columns=["Round", "Arousal", "Valance", "Max_A", "Min_A", "Max_V", "Min_V"])

        # Load FaceChannel Model and Training Manager
        global sess
        global graph

        with graph.as_default():
            tf.compat.v1.keras.backend.set_session(sess)

            self.face_channel = FaceChannelV1(type="Dim")

            if self.train_cl:
                from .CLTrainManager import TrainManager

                self.training_manager: TrainManager = TrainManager(sess, graph, experiment_gwrs, self.face_channel)

        # Clean log directory if it exists. Then, create empty folders.
        if os.path.isdir(self.log_dir):
            shutil.rmtree(self.log_dir)

        os.mkdir(self.log_dir)

        self.generate_round_folders()

        self._faces = []

        # Create LOG files
        self.log_face_channel.to_csv(self.log_face_channel_path)
        self.log_cl.to_csv(self.log_cl_path)

    def start(self):
        """
            Start
        :return: None
        """

        self._faces = []

    def close(self):
        """
            Close session and threads
        :return: None
        """
        self._faces = []
        if hasattr(self, "training_manager"):
            self.training_manager.wait()
            self.training_manager.stop()

        max_for_user = {
            "max_a": float(self.max_a),
            "max_v": float(self.max_v),
            "min_a": float(self.min_a), 
            "min_v": float(self.min_v)
        }

        with open(os.path.join(SESSIONS_DIR, f"arousal_valance/") + self.participant_name + ".json", "w") as file:
            json.dump(max_for_user, file)
    
    @abstractmethod
    def get_valid_faces(self, predictions: list) -> list:
        """
            Return the valid faces to imagine
        :param predictions: FaceChannel prediction.
        :return: Valid Face path list
        """

    def stop(self) -> list:
        """
            It runs FaceChannel and CL Model.
        :return: Prediction of the model
        """

        # Current Round Folder
        round_dir = self.round_dir % self.round

        #  Training and Prediction Phrase
        global sess
        global graph

        with graph.as_default():
            tf.compat.v1.keras.backend.set_session(sess)
            if self.session_type == "face_channel_only":
                predictions = self.predict_face_channel(np.array(self._faces, dtype=np.float32), True)
                self._faces = []  # Clean Faces
            elif self.session_type == "face_channel":
                predictions = self.predict_face_channel(np.array(self._faces, dtype=np.float32), True)
                self._faces = []  # Clean Faces
                
                start_time = time.time()
                valid_faces = self.get_valid_faces(predictions)
                print("Cleaning (s): ", time.time() - start_time, "Number of valid faces:", len(valid_faces), " / ", len(predictions))

                self.training_manager.enqueue(round_dir, self.gwr_dir, self.round, valid_faces)
            elif self.session_type == "continual_learning":
                start_time = time.time()
                face_channel_predictions = self.predict_face_channel(np.array(self._faces, dtype=np.float32), False)
                self._faces = []  # Clean Faces
                print("FC_PRED_TIME: ", time.time() - start_time)

                start_time = time.time()
                predictions = self.predict_cl(round_dir)
                print("CL_PRED_TIME: ", time.time() - start_time)
                
                start_time = time.time()
                valid_faces = self.get_valid_faces(face_channel_predictions)
                print("Cleaning: ", time.time() - start_time, "Number of valid faces:", len(valid_faces), " / ", len(predictions))

                start_time = time.time()
                self.training_manager.enqueue(round_dir, self.gwr_dir, self.round, valid_faces)
                print("QUEUE_PRED_TIME: ", time.time() - start_time)

            elif self.session_type == "seven_emotions":
                self._faces = []  # Clean Faces

                predictions = self.predict_cl(round_dir)
                
                self.training_manager.enqueue(round_dir, self.gwr_dir, self.round)

            else: 
                print("Running Test Emotions")
                predictions = {"Valance": 0.5, "Arousal": 0.5,
                   "Max_V": 0.5, "Min_V": 0.5, "Max_A": 0.5, "Min_A": 0.5}

        # Round Update
        self.round += 1
        self.generate_round_folders()

        return predictions

    def predict_face_channel(self, faces: np.ndarray, update_min_max: bool) -> list:
        """
            Return the prediction of FaceChannel Model
        :param faces: Face images, Numpy Array
        :param update_min_max: Update Max and Min Valance and Arousal
        :return: Predictions
        """
        predictions = self.face_channel.predict(faces, preprocess=False)

        self._log_face_channel(predictions, update_min_max)

        return predictions

    def predict_cl(self, log_dir: str, update_min_max: bool = True) -> list:
        """
            Return the prediction of CL Model
        :param log_dir: Logging directory path for CL Model
        :param update_min_max: Update Max and Min Valance and Arousal
        :return: Predictions
        """
        global sess
        global graph

        if len(self.training_manager.models) > 0:
            model_copy = copy.deepcopy(self.training_manager.models[-1])
            predictions = self.prediction_from_cl(log_dir=log_dir, model=model_copy, sess=sess, graph=graph, face_channel=self.face_channel)

            if len(self.training_manager.models) > 2:
                first_cp = self.training_manager.models.pop(0)
                del first_cp

            self._log_cl(predictions, update_min_max)

            return predictions

        return [0., 0.]

    def generate_round_folders(self):
        """
            Generates round folders.
        :return: None
        """
        faces_dir = os.path.join(self.round_dir % self.round, "faces/")
        faces_cut_dir = os.path.join(self.round_dir % self.round, "faces_cut/")
        imagined_dir = os.path.join(self.round_dir % self.round, "imagined/")
        frames_dir = os.path.join(self.round_dir % self.round, "frames/")

        # Generate folders

        os.mkdir(self.round_dir % self.round)
        os.mkdir(faces_dir)
        os.mkdir(faces_cut_dir)
        os.mkdir(imagined_dir)
        os.mkdir(frames_dir)

    def _log_face_channel(self, predictions: list, update_min_max: bool = False):
        """
            Log prediction results into face_channel.csv
        :param data: Predictions
        :param update_min_max: Update Max and Min Valance and Arousal
        :return: None
        """

        if update_min_max:
            for i in range(len(predictions[0])):
                self.max_a = max(self.max_a, predictions[0][i][0])
                self.min_a = min(self.min_a, predictions[0][i][0])

                self.max_v = max(self.max_v, predictions[1][i][0])
                self.min_v = min(self.min_v, predictions[1][i][0])

        for i in range(len(predictions[0])):
            self.log_face_channel = self.log_face_channel.append({
                                                                  "Round": self.round,
                                                                  "Arousal": predictions[0][i][0],
                                                                  "Valance": predictions[1][i][0],
                                                                  "Max_A": self.max_a,
                                                                  "Min_A": self.min_a,
                                                                  "Max_V": self.max_v,
                                                                  "Min_V": self.min_v,
                                                                  },
                                                                 ignore_index=True)

        self.log_face_channel.to_csv(self.log_face_channel_path)

    def _log_cl(self, predictions: list, update_min_max: bool = True):
        """
            Log prediction results into cl.csv
        :param predictions: Predictions
        :param update_min_max: Update Max and Min Valance and Arousal
        :return: None
        """

        if update_min_max:
            for i in range(len(predictions)):
                self.max_a = max(self.max_a, predictions[i][0][0][0])
                self.min_a = min(self.min_a, predictions[i][0][0][0])

                self.max_v = max(self.max_v, predictions[i][1][0][0])
                self.min_v = min(self.min_v, predictions[i][1][0][0])

        for i in range(len(predictions)):
            self.log_cl = self.log_cl.append({
                                              "Round": self.round,
                                              "Arousal": predictions[i][0][0][0],
                                              "Valance": predictions[i][1][0][0],
                                              "Max_A": self.max_a,
                                              "Min_A": self.min_a,
                                              "Max_V": self.max_v,
                                              "Min_V": self.min_v,
                                              },
                                             ignore_index=True)

        self.log_cl.to_csv(self.log_cl_path)

