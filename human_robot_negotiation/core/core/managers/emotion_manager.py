import json

from .abstract_manager import AbstractManager
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue


class EmotionManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def start_camera(self):
        self.queue_manager.send_message(HANTQueue.EMOTION.value, json.dumps({
            "action": "start_recording"
        }))

    def stop_camera(self):
        self.queue_manager.send_message(HANTQueue.EMOTION.value, json.dumps({
            "action": "stop_recording"
        }))

    def get_predictions(self):
        res = self.queue_manager.wait_for_message_from_queue(HANTQueue.EMOTION.value)
        return res["predictions"], res["normalized_predictions"]
