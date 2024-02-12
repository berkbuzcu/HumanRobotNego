from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from .abstract_manager import AbstractManager


class LoggerManager(AbstractManager):
    queue_handler: MultiQueueHandler

    def log(self, msg):
        self.queue_handler.send_message(HANTQueue.LOGGER, msg)
