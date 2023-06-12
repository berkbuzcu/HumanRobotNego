from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QComboBox, QFileDialog, QHBoxLayout, QLineEdit
from PySide6.QtGui import QMovie, QIcon

from human_robot_negotiation.HANT.preference_elicitation import PreferenceElicitation
from human_robot_negotiation import DOMAINS_DIR

import traceback

class DomainSelect(QWidget):
    def __init__(self, agent_type, callback_func):
        super(DomainSelect, self).__init__()

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Preference Profile of " + agent_type))
        
        self.callback_func = callback_func
        self.agent_type = agent_type

        self.selected_file_label = QLabel("")
        layout.addWidget(self.selected_file_label)
        
        self.select_domain_button = QPushButton("...")
        self.select_domain_button.setFixedWidth(40)
        self.select_domain_button.pressed.connect(self.emit_callback)

        layout.addWidget(self.select_domain_button)

        self.setLayout(layout)

    def emit_callback(self):
        self.callback_func(self.agent_type)

    def update_text(self, text):
        self.selected_file_label.setText(text)


form_fields = {
    "Session Type": ["Demo", "Session 1", "Session 2"],
    "Agent Type": ["DemoHybrid", "Hybrid", "Solver"],
    "Output Type": ["Pepper+GUI","Nao+GUI","Test+GUI"],
    "Input Type": ["Speech", "Text"],
    "Facial Expression Model": ["face_channel_only", "None"],
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

class ConfigManager(QMainWindow):
    def __init__(self, tool):
        super(ConfigManager, self).__init__()
        
        self.tool = tool

        self.setWindowTitle("HANT Config Manager")
        self.setWindowIcon(QIcon("head-of-nao-robot.jpg"))

        self.counter = 0
        layout = QVBoxLayout()

        self.setFixedWidth(400)
    
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

        self.setCentralWidget(central_widget)

        self.loading = LoadingScreen(tool.screens()[-1])       

    def select_file_dialog(self, agent_type):
        dialog = QFileDialog(self, ("Select a Preference Profile"), str(DOMAINS_DIR / self.domain_dropdown.currentText() / self.name_field.text()))
        if dialog.exec():
            agent_type = agent_type.lower()
            selected_domain = str(dialog.selectedFiles()[0])
            self.parameters[f"{agent_type}-domain"] = selected_domain
            getattr(self, f"{agent_type}_domain").update_text("/".join(selected_domain.split("/")[-3:]))

    def show_elicitation(self):
        self.pref_elicitation = PreferenceElicitation(self.name_field.text(), str(DOMAINS_DIR / self.domain_dropdown.currentText() / f"{self.domain_dropdown.currentText()}.xml"))
        self.pref_elicitation.show()

    def start_nego(self):
        try:
            self.start_button.setDisabled(True)

            self.parameters["Participant Name"] = self.name_field.text()
            self.parameters["Deadline"] = int(self.deadline_field.text())
            self.parameters["Domain"] = self.domain_dropdown.currentText()
            
            self.parameters = {**self.parameters, **{key: value.currentText() for key, value in self.values.items()}}
            
            if "+" in self.parameters["Output Type"]:
                self.parameters["Output Type"] = self.parameters["Output Type"].split("+")[0]

            self.tool.negotiation_setup(self.parameters)

        except Exception as e:
            traceback.print_exc()
            self.start_button.setDisabled(False)
    
    def reset_manager(self):
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


