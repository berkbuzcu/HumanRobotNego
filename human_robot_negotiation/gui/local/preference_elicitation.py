from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QLabel, QMainWindow, QVBoxLayout, QBoxLayout, \
    QGridLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QMimeData, Signal, QPoint, QDir
from PySide6.QtGui import QDrag, QPixmap, QFont, QIcon
import math
from human_robot_negotiation.core.utility_space_controller import UtilitySpaceController
import numpy as np
from xml.dom import minidom


class DragItem(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")

        self.setFixedWidth(160)
        # Store data separately from display label, but use label for default.
        self.data = self.text()

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.MoveAction)


class DragWidget(QWidget):
    orderChanged = Signal(list)

    def __init__(self, items):
        super().__init__()
        self.setAcceptDrops(True)

        self.blayout = QHBoxLayout()

        for n, l in enumerate(items):
            item = DragItem(l)
            item.set_data(l)  # Store the data.
            self.blayout.addWidget(item)

        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos: QPoint = e.pos()
        widget = e.source()

        chosen_spot = 0
        closest_dist = 99999999
        for n in range(self.blayout.count()):
            w = self.blayout.itemAt(n).widget()

            if not isinstance(w, DragItem):
                continue

            dist = math.dist((pos.x(), pos.y()), (w.x(), w.y()))

            if dist < closest_dist:
                closest_dist = dist
                chosen_spot = n
                if w.x() > pos.x():
                    chosen_spot -= 1

        self.blayout.insertWidget(chosen_spot, widget)
        self.orderChanged.emit(self.get_item_data())

        e.accept()

    def get_item_data(self):
        data = []
        for n in range(self.blayout.count()):
            w = self.blayout.itemAt(n).widget()
            data.append(w.data)
        return data


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class OrderLabels(QWidget):
    def __init__(self, label_size) -> None:
        super().__init__()

        label_layout = QHBoxLayout()

        for i in range(label_size):
            label = QLabel(f"{i + 1}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedWidth(160)
            label_layout.addWidget(label)

        self.setLayout(label_layout)


class PreferenceElicitation(QMainWindow):
    def __init__(self, negotiator_name, domain_file):
        super().__init__()

        self.negotiator_name = negotiator_name
        self.setWindowTitle("Human Agent Negotiation Framework")
        self.setWindowIcon(QIcon("head-of-nao-robot.jpg"))

        container = QWidget()
        layout = QGridLayout()

        self.utility_space_controller = UtilitySpaceController(domain_file)
        self.issue_values_widgets = {}

        font = QFont()
        font.setBold(True)

        line_row = 0

        title_font = QFont("Helvetica", 15, QFont.Bold)
        title_label = QLabel("Preference Elicitation")
        title_label.setFont(title_font)
        title_label.setContentsMargins(0, 10, 0, 10)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label, line_row, 0, 1, 8)
        line_row += 1

        issue_ordering_label = QLabel("Issue Ordering")
        issue_ordering_label.setFont(QFont("Helvetica", 10, QFont.Bold))
        layout.addWidget(issue_ordering_label, line_row, 0, 1, 8)
        line_row += 1

        instruction_label = QLabel("Drag the items to order them from 1 (most important) to 4 (least important)")
        instruction_label.setFont(font)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instruction_label, line_row, 0, 1, 8)
        line_row += 1

        layout.addWidget(OrderLabels(len(self.utility_space_controller.issue_values_list.keys())), line_row, 2, 1, 5)
        line_row += 1

        widgets = {"Issues": self.utility_space_controller.issue_values_list.keys(),
                   **self.utility_space_controller.issue_values_list}
        for row, (issue, values) in enumerate(widgets.items()):
            # if row == 0:
            #    layout.addWidget(QHLine(), line_row, 0, 1, 8)
            #    line_row += 1

            if row == 1:
                layout.addWidget(QHLine(), line_row, 0, 1, 8)
                line_row += 1
                value_ordering_label = QLabel("Value Ordering")
                value_ordering_label.setFont(QFont("Helvetica", 10, QFont.Bold))
                layout.addWidget(value_ordering_label, line_row, 0, 1, 8)
                line_row += 1
                instruction_label = QLabel(
                    "Drag the items to order them from 1 (most preferred) to 4 (least preferred)")
                instruction_label.setFont(font)
                instruction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                layout.addWidget(instruction_label, line_row, 0, 1, 8)
                line_row += 1
                layout.addWidget(OrderLabels(len(self.utility_space_controller.issue_values_list.keys())), line_row, 2,
                                 1, 5)
                line_row += 1

            issue_label = QLabel(issue + ":")
            issue_label.setFont(font)
            issue_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(issue_label, line_row, 1)
            self.value_widget = DragWidget(values)
            layout.addWidget(self.value_widget, line_row, 2, 1, 5)

            self.issue_values_widgets[issue] = self.value_widget

            line_row += 1

        self.submit_button = QPushButton("Submit")
        self.submit_button.pressed.connect(self.get_preferences)
        layout.addWidget(self.submit_button, (row + 2) * 2 + 4, 6)

        container.setLayout(layout)

        self.setCentralWidget(container)

    def get_preferences(self):
        ...

    def create_xml(self, negotiator_type, preference_dict):
        ...
