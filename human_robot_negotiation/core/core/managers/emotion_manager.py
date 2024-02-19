import json

from .abstract_manager import AbstractManager
from queuelib.queue_manager import MultiQueueHandler
from queuelib.message import EmotionMessage
from queuelib.enums import HANTQueue


class EmotionManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def start_camera(self):
        message = EmotionMessage("CORE", {"action": "start_recording"}, "recording")
        self.queue_manager.send_message(message)

    def stop_camera(self):
        message = EmotionMessage("CORE", {"action": "stop_recording"}, "recording")
        self.queue_manager.send_message(message)

        res = self.queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION)
        return res.payload["predictions"], res.payload["normalized_predictions"]
