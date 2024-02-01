from queuelib.queue_manager import MultiQueueHandler
from queuelib.enums import HANTQueue


queue_handler = MultiQueueHandler([e for e in HANTQueue])
