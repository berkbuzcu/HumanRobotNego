
from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue
from queuelib.message import CameraMessage
import time
camera_id = "0"

# Load Camera Capturing
queue_manager = MultiQueueHandler([HANTQueue.CAMERA], host="localhost")

msg = CameraMessage("CAMERA", {"username": "berk buzcu"}, status=True)
queue_manager.send_message(msg)
time.sleep(2)
msg = CameraMessage("CAMERA", {"action": "start_recording"}, status=True)
queue_manager.send_message(msg)

time.sleep(5)

msg = CameraMessage("CAMERA", {"action": "stop_recording"}, status=True)
queue_manager.send_message(msg)