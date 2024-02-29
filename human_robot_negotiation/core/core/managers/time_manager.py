import threading
import time


class TimeManager:
    def __init__(self, duration, callback):
        self.duration = duration
        self.callback = callback
        self._running = False

    def start(self):
        self._running = True
        thread = threading.Thread(target=self._countdown)
        thread.start()

    def stop(self):
        self._running = False

    def get_remaining_time(self):
        if not self._running:
            return 0
        return max(self.duration, (time.time() - self._start_time)) / self.duration

    def _countdown(self):
        self._start_time = time.time()
        while self._running and self.get_remaining_time() > 0:
            time.sleep(1)
        if self._running:
            self.callback()