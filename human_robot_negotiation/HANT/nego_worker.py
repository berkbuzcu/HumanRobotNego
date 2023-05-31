from PySide6.QtCore import QRunnable, Slot, QThreadPool, QDir, QObject, Signal
import traceback
import sys


class WorkerSignals(QObject):
    finished = Signal()
    nego_over = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class NegotiationWorker(QRunnable):
    def __init__(self, tool):
        super(NegotiationWorker, self).__init__()

        self.signals = WorkerSignals()
        self.tool = tool

    @Slot() 
    def run(self):
        try:
            self.tool.negotiate()
            self.signals.finished.emit()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))