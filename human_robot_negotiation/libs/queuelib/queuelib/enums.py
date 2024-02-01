from enum import Enum


class HANTQueue(Enum):
    INTERNAL = "internal"
    ROBOT = "robot"
    GUI = "gui"
    EMOTION = "emotion"
    AGENT = "agent"
    LOGGER = "logger"
    HUMAN = "human"
