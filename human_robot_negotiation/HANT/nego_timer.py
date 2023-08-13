from PySide6.QtCore import QTimer, SIGNAL, Slot, Signal, QObject

class NegotiationTimer(QObject):
    start_signal = Signal()
    finish_signal = Signal()

    def __init__(self, deadline, timeout_callback):
        super().__init__()
        self.deadline = deadline

        self.remaining_time = 1.0

        self.main_timer = QTimer()
        self.main_timer.timeout.connect(timeout_callback) # timeout_callback is called on timeout
        self.main_timer.setSingleShot(True)

        self.repeater = QTimer(self)

        # Repeater will update time per the actual counter
        self.repeater.timeout.connect(self.update_time)

        self.finish_signal.connect(self.stop_timer)
        self.start_signal.connect(self.start_timer)

    def update_time(self):
        self.remaining_time = self.main_timer.remainingTime()

    def get_current_time(self) -> float:
        result = (self.remaining_time / 1000) / self.deadline
        print("REM T: ", (float(self.deadline) - self.remaining_time) / (float(self.deadline)))
        return result # self.counter: us -> s

    def get_remaining_time(self) -> float:
        print("DL: ", self.deadline, type(self.deadline))
        print("RT: ", self.remaining_time)
        print("RES: ", (float(self.deadline) - self.remaining_time) / (float(self.deadline)))
        return (float(self.deadline) - self.remaining_time) / (float(self.deadline)) # hack until i solve



    # Method is invoked by negotiations that end before timeout
    def stop_timer(self): 
        self.main_timer.stop()
        self.repeater.stop()

    def start_timer(self):
        print("STARTING TIMER")
        self.main_timer.start(self.deadline)
        self.repeater.start(1000)