from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QLabel, QMainWindow, QVBoxLayout, QBoxLayout, QGridLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QMimeData, Signal, QPoint, QDir
from PySide6.QtGui import QDrag, QPixmap, QFont, QIcon
import math
from human_robot_negotiation.HANT.utility_space_controller import UtilitySpaceController
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
            label = QLabel(f"{i+1}")
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
        #print("domdomfile: ", domain_file)
        #print("util controller: ", self.utility_space_controller.issue_values_list)
        self.issue_values_widgets = {}

        font = QFont()
        font.setBold(True)
    
        line_row = 0

        title_font = QFont("Helvetica", 15, QFont.Bold)
        title_label =  QLabel("Preference Elicitation")
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

        widgets = {"Issues": self.utility_space_controller.issue_values_list.keys(), **self.utility_space_controller.issue_values_list}
        for row, (issue, values) in enumerate(widgets.items()):      
            #if row == 0:
            #    layout.addWidget(QHLine(), line_row, 0, 1, 8)
            #    line_row += 1

            if row == 1:
                layout.addWidget(QHLine(), line_row, 0, 1, 8)
                line_row += 1
                value_ordering_label = QLabel("Value Ordering")
                value_ordering_label.setFont(QFont("Helvetica", 10, QFont.Bold))
                layout.addWidget(value_ordering_label, line_row, 0, 1, 8) 
                line_row += 1
                instruction_label = QLabel("Drag the items to order them from 1 (most preferred) to 4 (least preferred)")
                instruction_label.setFont(font)
                instruction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                layout.addWidget(instruction_label, line_row, 0, 1, 8)
                line_row += 1
                layout.addWidget(OrderLabels(len(self.utility_space_controller.issue_values_list.keys())), line_row, 2, 1, 5)
                line_row += 1
                

            issue_label = QLabel(issue+":")
            issue_label.setFont(font)
            issue_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(issue_label, line_row, 1)
            self.value_widget = DragWidget(values)
            layout.addWidget(self.value_widget, line_row, 2, 1, 5)
        
            self.issue_values_widgets[issue] = self.value_widget

            line_row += 1

        #layout.addWidget(QHLine(), line_row, 0, 1, 8)
        self.submit_button = QPushButton("Submit")
        self.submit_button.pressed.connect(self.get_preferences)
        layout.addWidget(self.submit_button, (row+2)*2+4, 6)

        container.setLayout(layout)

        self.setCentralWidget(container)

    def get_preferences(self):
        preference_dict = {}
        reversed_pref_dict = {}

        issue_values_ordered = {}
        issues_ordered = self.issue_values_widgets.pop("Issues").get_item_data()

        for issue, item in self.issue_values_widgets.items():
           issue_values_ordered[issue] = item.get_item_data()

        weight_sum = 0.

        issue_order_human = [i for i in range(len(issues_ordered))]
        issue_order_agent = issue_order_human.copy()

        for i in range(0, len(issue_order_human), 2):
            issue_order_agent[i], issue_order_agent[i + 1] = issue_order_agent[i + 1], issue_order_agent[i]

        for i in range(len(issues_ordered)):
            preference_dict[issues_ordered[i]] = {'weight': len(issues_ordered) - i}
            reversed_pref_dict[issues_ordered[i]] = {'weight': len(issues_ordered) - issue_order_agent[i]}

            weight_sum += i + 1

        for issue_name in issues_ordered:
            preference_dict[issue_name]["weight"] = np.round(preference_dict[issue_name]["weight"] / weight_sum * 100.) / 100.
            reversed_pref_dict[issue_name]["weight"] = np.round(reversed_pref_dict[issue_name]["weight"] / weight_sum * 100.) / 100.

        for i, issue_name in enumerate(issues_ordered):
            value_order_human = [j for j in range(len(issue_values_ordered[issue_name]))]
            value_order_agent = value_order_human.copy()
            value_order_agent[:len(value_order_human) // 2] = value_order_human[len(value_order_human) // 2:]
            if len(value_order_human) % 2 == 1:
                value_order_agent[len(value_order_human) // 2 + 1:] = value_order_human[:len(value_order_human) // 2]
            else:
                value_order_agent[len(value_order_human) // 2:] = value_order_human[:len(value_order_human) // 2]

            for j, value_name in enumerate(issue_values_ordered[issue_name]):
                preference_dict[issue_name][value_name] = len(issue_values_ordered[issue_name]) - j
                reversed_pref_dict[issue_name][value_name] = len(issue_values_ordered[issue_name]) - value_order_agent[j]

            for value_name in issue_values_ordered[issue_name]:
                preference_dict[issue_name][value_name] = np.round(preference_dict[issue_name][value_name] / len(issue_values_ordered[issue_name]) * 100.) / 100.
                reversed_pref_dict[issue_name][value_name] = np.round(reversed_pref_dict[issue_name][value_name] / len(issue_values_ordered[issue_name]) * 100.) / 100.


        self.create_xml("Human", preference_dict)
        self.create_xml("Agent", reversed_pref_dict)

        self.destroy()


    def create_xml(self, negotiator_type, preference_dict):
        root = minidom.Document()
        xml = root.createElement('negotiation_domain')
        root.appendChild(xml)

        utility_space = root.createElement('utility_space')
        utility_space.setAttribute('domain_name', self.utility_space_controller.domain_name)
        utility_space.setAttribute('domain_type', self.utility_space_controller.domain_type)
        utility_space.setAttribute('number_of_issues', str(len(preference_dict)))

        xml.appendChild(utility_space)

        issue_index = 1
        for issue_name, values in preference_dict.items():
            issue_weight = values.pop("weight")

            issue_weight_element = root.createElement('weight')
            issue_weight_element.setAttribute('index', str(issue_index))
            issue_weight_element.setAttribute('value', str(issue_weight))

            utility_space.appendChild(issue_weight_element)

            issue_element = root.createElement('issue')
            issue_element.setAttribute('index', str(issue_index))
            issue_element.setAttribute('name', str(issue_name))

            utility_space.appendChild(issue_element)

            issue_index += 1
            
            value_index = 1
            for value_name, value_weight in values.items():
                value_element = root.createElement('item')
                value_element.setAttribute('index', str(value_index))
                value_element.setAttribute('value', str(value_name))
                value_element.setAttribute('evaluation', str(value_weight))

                issue_element.appendChild(value_element)
                value_index += 1

        xml_str = root.toprettyxml(indent ="\t")

        dir = QDir(self.utility_space_controller.domain_file)
        dir.cdUp()
        
        cd_complete = dir.cd(self.negotiator_name)
        if not cd_complete:
            dir.mkdir(self.negotiator_name)
            dir.cd(self.negotiator_name)

        with open(dir.absolutePath() + f"/{negotiator_type}.xml", "w") as f:
            f.write(xml_str) 


if __name__ == "__main__":
    app = QApplication([])
    w = PreferenceElicitation("Berk", "HANT\Domains\Holiday_A\Holiday_A.xml")
    w.show()

    app.exec()  