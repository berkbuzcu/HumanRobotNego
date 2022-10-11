import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spry-water-357912-42ef44b257e5.json"

from email.charset import QP
from inspect import Parameter, trace
from PySide6.QtCore import QRunnable, Slot, QThreadPool, QDir, QObject, Signal
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QApplication, QComboBox, QFileSystemModel, QTreeView, QSplitter, QFileDialog, QHBoxLayout, QLineEdit
from PySide6.QtGui import QMovie, QIcon
from HANT.hant import HANT
import sys
import time
from gui.nego_gui import NegotiationGUI
import traceback
from preference_elicitation import PreferenceElicitation



class WorkerSignals(QObject):
    finished = Signal()
    nego_over = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)

class NegotiationWorker(QRunnable):
    def __init__(self, nego_configs, config_manager):
        super(NegotiationWorker, self).__init__()

        self.nego_configs = nego_configs
        self.config_manager = config_manager
        self.signals = WorkerSignals()

        self.tool = HANT(
            participant_name=self.nego_configs["Participant Name"],
            session_number=self.nego_configs["Session Type"],
            session_type=self.nego_configs["Facial Expression Model"],
            human_interaction_type=self.nego_configs["Input Type"],
            agent_interaction_type=self.nego_configs["Output Type"],
            agent_type=self.nego_configs["Agent Type"],
            agent_preference_file=self.nego_configs["agent-domain"],
            human_preference_file=self.nego_configs["human-domain"],
            domain_name=self.nego_configs["Domain"],
            log_file_path="./Logs/",
            config_manager=self.config_manager,
            stop_nego_signal=self.signals.nego_over
        )

    @Slot() 
    def run(self):
        try:
            self.tool.negotiate()
            self.signals.finished.emit()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))


class DomainSelect(QWidget):
    def __init__(self, agent_type, callback_func):
        super(DomainSelect, self).__init__()

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Preference Profile of " + agent_type))
        
        self.selected_file_label = QLabel("")
        layout.addWidget(self.selected_file_label)
        
        select_domain_button = QPushButton("...")
        select_domain_button.setFixedWidth(40)
        select_domain_button.pressed.connect(lambda: callback_func(agent_type))

        layout.addWidget(select_domain_button)

        self.setLayout(layout)

    def update_text(self, text):
        self.selected_file_label.setText(text)


form_fields = {
    "Session Type": ["Demo", "Session 1", "Session 2"],
    "Agent Type": ["Solver", "Hybrid", "DemoHybrid"],
    "Output Type": ["Nao+GUI","Test+GUI"],
    "Input Type": ["Speech", "Text"],
    "Facial Expression Model": ["continual_learning", "face_channel_only", "face_channel", "None"],
    "Protocol": ["Alternating Offer Protocol"],
    "Domain": ["Holiday_A", "Holiday_B", "Fruits", "Deserted Island"],
}

class LoadingScreen(QMainWindow):
    def __init__(self, screen) -> None:
        super().__init__()
        self.setWindowTitle("Finishing training...")
        self.setFixedSize(640, 480)
        self.setScreen(screen)
        self.move(screen.geometry().center())
        self.activateWindow()
        
        
        self.gif = QMovie("loading.gif")

        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setMovie(self.gif)

        self.setCentralWidget(self.label)

        self.gif.start()


class ConfigManager(QApplication):
    def __init__(self):
        super(ConfigManager, self).__init__()
        
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("HANT Config Manager")
        self.main_window.setWindowIcon(QIcon("head-of-nao-robot.jpg"))

        self.counter = 0
        layout = QVBoxLayout()

        self.main_window.setFixedWidth(400)
    
        self.values = {}
        self.parameters = {}

        self.name_field = QLineEdit("")
        layout.addWidget(QLabel("Participant Name"))
        layout.addWidget(self.name_field)
        
        self.deadline_field = QLineEdit("")
        layout.addWidget(QLabel("Deadline"))        
        layout.addWidget(self.deadline_field)

        domain_fields = form_fields.pop("Domain")

        for text, values in form_fields.items():
            label = QLabel(text)
            widget = QComboBox()
            self.values[text] = widget
            widget.addItems(values)
            layout.addWidget(label)
            layout.addWidget(widget)
        
        layout.addWidget(QLabel("Domain"))
        domain_layout = QHBoxLayout()
        self.domain_dropdown = QComboBox()
        self.domain_dropdown.addItems(domain_fields)

        preference_elicitation_button = QPushButton("...")
        preference_elicitation_button.pressed.connect(self.show_elicitation)
        domain_layout.addWidget(self.domain_dropdown)
        domain_layout.addWidget(preference_elicitation_button)

        layout.addItem(domain_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.domain_dir = QDir("HANT/Domains/").absolutePath()

        self.agent_domain = DomainSelect("Agent", self.select_file_dialog)
        self.human_domain = DomainSelect("Human", self.select_file_dialog)

        layout.addWidget(self.agent_domain)
        layout.addWidget(self.human_domain)

        #self.stop_button = QPushButton("...")
        #self.stop_button.setFixedWidth(40)
        #self.stop_button.pressed.connect(self.kill_nego)
        #layout.addWidget(self.stop_button)

        self.start_button = QPushButton("Start")
        self.start_button.pressed.connect(self.start_nego)
        layout.addWidget(self.start_button)

        self.main_window.setCentralWidget(central_widget)

        self.threadpool = QThreadPool()
        self.loading = LoadingScreen(self.screens()[1])       

        self.main_window.show()

    def start_nego(self):
        try:
            self.start_button.setDisabled(True)
            self.parameters["Participant Name"] = self.name_field.text()
            self.parameters["Deadline"] = int(self.deadline_field.text())
            self.parameters["Domain"] = self.domain_dropdown.currentText()

            self.nego_window = NegotiationGUI(self.screens()[1], self.parameters["Deadline"] * 1000, self.nego_timeout)
            #self.nego_window.show()

            self.parameters = {**self.parameters, **{key: value.currentText() for key, value in self.values.items()}}

            if "+" in self.parameters["Output Type"]:
                self.parameters["Output Type"] = self.parameters["Output Type"].split("+")[0]

            self.negotiation_worker = NegotiationWorker(self.parameters, self)
            self.negotiation_worker.signals.nego_over.connect(self.nego_over)
            self.negotiation_worker.signals.finished.connect(self.cleanup_nego)
            self.threadpool.start(self.negotiation_worker)
            #self.nego_window.get_time_controller().start()
        except Exception as e:
            traceback.print_exc()
            self.start_button.setDisabled(False)
    
    def nego_over(self):
        self.nego_window.timer_widget.finish()
        self.loading.show()
        print("NEGO IS OVER!!!")

    def cleanup_nego(self):
        self.loading.destroy()
        self.nego_window.destroy()
        self.start_button.setDisabled(False)
    
    def kill_nego(self):
        self.negotiation_worker.tool.terminate_nego()

    def nego_timeout(self):
        self.negotiation_worker.tool.timeout_negotiation()

    def select_file_dialog(self, agent_type):
        dialog = QFileDialog(self.main_window, ("Select a Preference Profile"), self.domain_dir + "/" + self.domain_dropdown.currentText() + "/" + self.name_field.text())
        if dialog.exec():
            agent_type = agent_type.lower()
            selected_domain = str(dialog.selectedFiles()[0])
            self.parameters[f"{agent_type}-domain"] = selected_domain
            getattr(self, f"{agent_type}_domain").update_text(selected_domain)

    def show_elicitation(self):
        self.pref_elicitation = PreferenceElicitation(self.name_field.text(), self.domain_dir + "/" + self.domain_dropdown.currentText() + "/" + self.domain_dropdown.currentText() + ".xml")
        self.pref_elicitation.show()

config_manager = ConfigManager()
config_manager.exec()