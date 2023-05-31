from PySide6.QtCore import QTimer, SIGNAL

class NegotiationTimer(QTimer):
    def __init__(self, deadline, timeout_callback):
        super().__init__()

        self.deadline = deadline

        self.timeout.connect(timeout_callback) # timeout_callback is called on timeout
        self.setSingleShot(True)

    def get_current_time(self) -> float:
        result = (self.remainingTime() / 1000) / self.deadline
        return result # self.counter: us -> s

    def get_remaining_time(self) -> float:
        return (float(self.deadline) - self.remainingTime()) / (float(self.deadline)) # hack until i solve


    # Method is invoked by negotiations that end before timeout
    def stop_timer(self): 
        self.stop()

    def start_timer(self):
        self.start(self.deadline)