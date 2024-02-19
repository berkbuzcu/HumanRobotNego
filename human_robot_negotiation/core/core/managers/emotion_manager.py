import json

from .abstract_manager import AbstractManager
from queuelib.queue_manager import MultiQueueHandler
from queuelib.message import EmotionMessage, CameraMessage
from queuelib.enums import HANTQueue


class EmotionManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def start_camera(self):
        #message = EmotionMessage("CORE", {"action": "start_recording"}, "recording")
        #self.queue_manager.send_message(message)
        pass

    def stop_camera(self):
        #message = EmotionMessage("CORE", {"action": "stop_recording"}, "recording")
        #self.queue_manager.send_message(message)

        #res = self.queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)

        return {"Valance": 0.5, "Arousal": 0.5,
                                   "Max_V": 0.5, "Min_V": 0.5, "Max_A": 0.5, "Min_A": 0.5}, \
                {"Valance": 0.5, "Arousal": 0.5,
                                   "Max_V": 0.5, "Min_V": 0.5, "Max_A": 0.5, "Min_A": 0.5}
