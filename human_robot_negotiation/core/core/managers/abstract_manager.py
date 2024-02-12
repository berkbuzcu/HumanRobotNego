from abc import ABC, abstractmethod

from queuelib.queue_manager import MultiQueueHandler


class AbstractManager(ABC):
    queue_manager: MultiQueueHandler

    def __init__(self):
        self.queue_manager = MultiQueueHandler()
