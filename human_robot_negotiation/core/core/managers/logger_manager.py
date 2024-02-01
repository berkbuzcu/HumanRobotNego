from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue


class LoggerManager:
    def __init__(self):
        self.queue_handler = MultiQueueHandler()

    def log(self, msg):
        self.queue_handler.send_message(HANTQueue.LOGGER, msg)
