import copy
import typing as t

from .AbstractSession import *
from .Capturing import Capturing

class SessionCamera(AbstractSession):
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

    def __run_capturing(self):
        """
            Recording Thread
            Do not call it directly.
        :return: None
        """
        #global sess
        #global graph

        counter = 0

        #with graph.as_default():
        #    tf.compat.v1.keras.backend.set_session(sess)
        while (self._capturing):
            face = self.get_face(counter)
            counter += 1

            if face is None:
                continue

            self._faces.append(face)        
            

    def start(self):
        """
            Start Recording thread
        :return: None
        """
        super(SessionCamera, self).start()

        self._capturing = True

        self.thread_capturing = Thread(target=self.__run_capturing)
        self.thread_capturing.start()

    def close(self):
        """
            Close session and threads
        :return: None
        """
        self.close_camera()

        super(SessionCamera, self).close()
        
    def get_valid_faces(self, predictions: list) -> list:
        # Get Stats of the FaceChannel prediction of the current round
        mean_arousal = float(np.mean(predictions[0]))
        std_arousal = float(np.std(predictions[0]))
                
        mean_valance = float(np.mean(predictions[1]))
        std_valance = float(np.std(predictions[1]))
        
        valid_faces = []
        for i in range(len(predictions[0])):
            # If the arousal and valance of that image is close to mean, ignore it.
            if mean_arousal - std_arousal <= predictions[0][i][0] <= mean_arousal + std_arousal and mean_valance - std_valance <= predictions[1][i][0] <= mean_valance + std_valance:
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
        if not self._capturing:  # If it is not running, return empty predictions.
            print("No Capturing!!!!!!!!!!!")
            self.round += 1
            self.generate_round_folders()
            
            results = {
                "Arousal": 0.,
                "Valance": 0.,
                "Max_A": float(self.max_a),
                "Min_A": float(self.min_a),
                "Max_V": float(self.max_v),
                "Min_V": float(self.min_v),
            }
            return results, results #padding result

        #  Close Thread
        self._capturing = False
        self.thread_capturing.join(timeout=0.1)

        predictions = super(SessionCamera, self).stop()

        if self.session_type == "face_channel" or self.session_type == "face_channel_only":
            results = {
                "Arousal": float(np.mean(predictions[0])),
                "Valance": float(np.mean(predictions[1])),
                "Max_A": float(self.max_a),
                "Min_A": float(self.min_a),
                "Max_V": float(self.max_v),
                "Min_V": float(self.min_v),
            }
            return results, results
        else:
            result = {
                "Arousal": float(np.mean(np.array(predictions, dtype=np.float32)[:,0])),
                "Valance": float(np.mean(np.array(predictions, dtype=np.float32)[:,1])),
                "Max_A": float(self.max_a),
                "Min_A": float(self.min_a),
                "Max_V": float(self.max_v),
                "Min_V": float(self.min_v),
            }

            normalized_result = copy.deepcopy(result)
            normalized_result["Arousal"] = 2 * ((normalized_result["Arousal"] - self.min_a)/(self.max_a - self.min_a)) - 1 
            normalized_result["Valance"] = 2 * ((normalized_result["Valance"] - self.min_v)/(self.max_v - self.min_v)) - 1 

            return result, normalized_result

    def get_face(self, id: int) -> np.ndarray:
        """
            Run Session's camera and return Face as Numpy Array
        :param id: Frame Index
        :return: Face Image
        """
        face = self.capturing.run(id)
        
        if face is None:
            return None

        return np.array(face, dtype=np.float32)

    def generate_round_folders(self):
        """
            Generates round folders.
        :return: None
        """
        faces_dir = os.path.join(self.round_dir % self.round, "faces/")
        faces_cut_dir = os.path.join(self.round_dir % self.round, "faces_cut/")
        frames_dir = os.path.join(self.round_dir % self.round, "frames/")

        super(SessionCamera, self).generate_round_folders()

        # Capturing Formats

        self.capturing.save_path_format = faces_dir + "image_frame_%d.jpg"
        self.capturing.save_cut_path_format = faces_cut_dir + "image_frame_%d.jpg"
        self.capturing.save_frame_path_format = frames_dir + "image_frame_%d.jpg"

    def close_camera(self):
        """
            Close camera at the end of session
        :return: None
        """

        if self._capturing:
            self._capturing = False
            self.thread_capturing.join(timeout=0.1)

        self.capturing.close()

        self._faces = []

