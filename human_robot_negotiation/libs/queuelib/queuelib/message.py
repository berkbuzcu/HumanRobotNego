import json
from abc import ABC
from dataclasses import dataclass, asdict, field

from queuelib.enums import HANTQueue


@dataclass
class AbstractMessage(ABC):
    sender: str
    payload: dict
    context: str = None
    status: bool = True
    queue_type: HANTQueue = field(init=False)

    def to_json(self) -> str:
        as_dict = asdict(self)
        as_dict["queue_type"] = self.queue_type.to_json()
        return json.dumps(as_dict)

    @classmethod
    def from_json(cls, json_str):
        message_dict: dict = json.loads(json_str)

        class_switch = {
            HANTQueue.ROBOT.value: RobotMessage,
            HANTQueue.AGENT.value: AgentMessage,
            HANTQueue.EMOTION.value: EmotionMessage,
            HANTQueue.GUI.value: GUIMessage,
            HANTQueue.LOGGER.value: LoggerMessage,
            HANTQueue.CONFIG.value: ConfigMessage,
            HANTQueue.CAMERA.value: CameraMessage,
            HANTQueue.MICROPHONE.value: MicrophoneMessage,
        }

        return class_switch[message_dict.pop("queue_type")](**message_dict)


class RobotMessage(AbstractMessage):
    queue_type = HANTQueue.ROBOT


class AgentMessage(AbstractMessage):
    queue_type = HANTQueue.AGENT


class EmotionMessage(AbstractMessage):
    queue_type = HANTQueue.EMOTION


class GUIMessage(AbstractMessage):
    queue_type = HANTQueue.GUI


class LoggerMessage(AbstractMessage):
    queue_type = HANTQueue.LOGGER


class ConfigMessage(AbstractMessage):
    queue_type = HANTQueue.CONFIG


class HumanMessage(AbstractMessage):
    queue_type = HANTQueue.HUMAN


class MicrophoneMessage(AbstractMessage):
    queue_type = HANTQueue.MICROPHONE


class CameraMessage(AbstractMessage):
    queue_type = HANTQueue.CAMERA
