
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import MicrophoneMessage
import time

# Load Camera Capturing
queue_manager = MultiQueueHandler([HANTQueue.CAMERA], host="localhost")

msg = MicrophoneMessage("MICROPHONE", {"action": "get_recording"}, status=True)
queue_manager.send_message(msg)
time.sleep(1)
queue_manager.send_message(msg)
time.sleep(3)

msg = MicrophoneMessage("MICROPHONE", {"action": "stop_recording"}, status=True)
queue_manager.send_message(msg)