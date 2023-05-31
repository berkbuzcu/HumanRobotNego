from email.charset import QP
from inspect import Parameter
from PySide6.QtCore import QRunnable, Slot, QThreadPool, QDir, QObject, Signal
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QApplication, QComboBox, QFileSystemModel, QTreeView, QSplitter, QFileDialog, QHBoxLayout, QLineEdit
from human_robot_negotiation.HANT.hant import HANT
import sys
import time
from human_robot_negotiation.gui.nego_gui import NegotiationGUI
import traceback
from preference_elicitation import PreferenceElicitation

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class NegotiationWorker(QRunnable):
    def __init__(self):
        super(NegotiationWorker, self).__init__()

        self.signals = WorkerSignals()


    def negotiate():
        for i in range(90000):
            pass

        return

    @Slot() 
    def run(self):
        try:
            self.negotiate()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))


