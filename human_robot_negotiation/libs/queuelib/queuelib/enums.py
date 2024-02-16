from enum import Enum


class HANTQueue(Enum):
    CONFIG = "config"
    ROBOT = "robot"
    GUI = "gui"
    EMOTION = "emotion"
    AGENT = "agent"
    LOGGER = "logger"
    HUMAN = "human"
    MICROPHONE = "microphone"
    CAMERA = "camera"

    def to_json(self):
        return self.value
