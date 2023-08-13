from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QComboBox, QFileDialog, QHBoxLayout, QLineEdit, QMessageBox
from PySide6.QtGui import QMovie, QIcon

from human_robot_negotiation.HANT.preference_elicitation import PreferenceElicitation
from human_robot_negotiation import DOMAINS_DIR
from human_robot_negotiation.gui.camera.camera import Camera
from human_robot_negotiation.HANT.exceptions import CameraException

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
    "Agent Type": ["Hybrid", "Solver"],
    "Output Type": ["Pepper+GUI","Nao+GUI"],
    "Input Type": ["Speech", "Text"],
    "Facial Expression Model": ["face_channel_only"],
    "Protocol": ["Alternating Offer Protocol"],
    "Domain": ["Holiday_Demo", "Holiday_A","Holiday_B"],
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
        
        """self.deadline_field = QLineEdit("600")
        layout.addWidget(QLabel("Deadline"))        
        layout.addWidget(self.deadline_field)"""

        domain_fields = form_fields.pop("Domain")

        self.robot_name_field = QLineEdit("")

        def update_robot_name_field(name):
            self.robot_name_field.setText(name.split("+")[0])

        for text, values in form_fields.items():
            if text=="Input Type" or text=="Facial Expression Model" or text == "Protocol":
                label = QLabel(text)
                widget = QComboBox()
                self.values[text] = widget
                widget.addItems(values)
                
            elif not text=="Agent Type":
                label = QLabel(text)
                widget = QComboBox()

                if text == "Output Type":
                    widget.currentTextChanged.connect(update_robot_name_field)

                self.values[text] = widget
                widget.addItems(values)
                layout.addWidget(label)
                layout.addWidget(widget)

        layout.addWidget(QLabel("Robot Name"))
        layout.addWidget(self.robot_name_field)

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

        self.loading = LoadingScreen(tool.screens()[-1])     

        #self.start_button = QPushButton("Start")
        #self.start_button.pressed.connect(self.start_nego)

        self.camera_index = 0

        self.start_button = QPushButton("Start")
        self.start_button.pressed.connect(self.set_camera_dialog)
        layout.addWidget(self.start_button)

        self.setCentralWidget(central_widget)

    def set_camera_id(self, camera_id):
        self.camera_id = camera_id
        self.camera_preview.close()
        self.start_nego()

    def set_camera_dialog(self):
        self.camera_preview = Camera(self.set_camera_id)
        self.camera_preview.show()

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
            #self.parameters["Deadline"] = int(self.deadline_field.text())
            self.parameters["Deadline"] = 600 if self.values["Session Type"].currentText() == "Demo" else 900
            self.parameters["Domain"] = self.domain_dropdown.currentText()
            self.parameters["Agent Type"] = "Hybrid" if self.values["Session Type"].currentText() == "Demo" else "Solver"
            self.parameters["Robot Name"] = self.robot_name_field.text()
            self.parameters = {**self.parameters, **{key: value.currentText() for key, value in self.values.items()}}
            self.parameters["Camera ID"] = self.camera_id
            
            if "+" in self.parameters["Output Type"]:
                self.parameters["Output Type"] = self.parameters["Output Type"].split("+")[0]

            self.tool.negotiation_setup(self.parameters)
        except KeyError:
            msgBox = QMessageBox()
            msgBox.setText("Check all the fields.")
            msgBox.exec()
        except CameraException:
            msgBox = QMessageBox()
            msgBox.setText("Error with the camera (make sure all other applications are closed)")
            msgBox.exec()
        except Exception as e:
            traceback.print_exc()
        finally:
            self.start_button.setDisabled(False)
    
    def reset_manager(self):
        self.start_button.setDisabled(False)


