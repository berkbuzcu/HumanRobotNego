import threading
import time


class NegotiationTimer:
    def __init__(self, deadline, timeout_callback):
        self.start_time = None
        self.deadline = deadline
        self.remaining_time = 1.0
        self.timeout_callback = timeout_callback
        self.is_running = False
        self.timer_thread = None

    def update_time(self):
        self.remaining_time = max(0, self.deadline - (time.time() * 1000 - self.start_time))
        if self.remaining_time == 0:
            self.timeout_callback()

    def get_current_time(self) -> float:
        return (self.deadline - self.remaining_time) / 1000

    def get_remaining_time(self) -> float:
        return self.remaining_time / 1000

    def stop_timer(self):
        self.is_running = False
        self.timer_thread.join()

    def start_timer(self):
        print("STARTING TIMER")
        self.is_running = True
        self.start_time = time.time() * 1000
        self.timer_thread = threading.Thread(target=self._timer_thread)
        self.timer_thread.start()

    def _timer_thread(self):
        while self.is_running and self.remaining_time > 0:
            time.sleep(1)
            self.update_time()

        if self.is_running:
            self.timeout_callback()
