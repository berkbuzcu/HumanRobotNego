import sys
import copy
from PySide6.QtCore import QSize, Qt, QTimer, SIGNAL, QTime, QMargins, QAbstractTableModel, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QTableView, QHeaderView, QAbstractItemView, QHBoxLayout, QFrame
from PySide6.QtGui import QPalette, QColor, QFont, QFontMetrics, QPainter, QBrush, QPageSize

#from utilitySpace import UtilitySpace

def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(list(item).pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError): # deleted or no close method
            pass
        try:
            item.deleteLater()
        except (RuntimeError, AttributeError): # deleted or no deleteLater method
            pass
# end clean

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class Timer(QLabel):
    def __init__(self, timer):
        super(Timer, self).__init__()

        repeater = QTimer(self)

        # Repeater will update time per the actual counter
        self.connect(repeater, SIGNAL('timeout()'), self.update_time)
        repeater.start(1000)

        self.timer = timer

        self.setAlignment(Qt.AlignCenter)
        
        font_style = QFont("Helvetica", 20)
        font_style.setBold(True)

        self.setFont(font_style)

        metrics = QFontMetrics(font_style)

        self.setStyleSheet("border: 1px solid black;")
        self.setFixedHeight(120)
        #self.setFixedWidth(400)

    def update_time(self):
        time_micro_seconds = self.timer.main_timer.remainingTime()
        time_seconds = (time_micro_seconds / 1000)
        time_minutes = time_seconds // 60
        time_left_seconds = time_seconds % 60
        self.setText("Time: " + str(f"{str(int(time_minutes)).zfill(2)}: {str(int(time_left_seconds)).zfill(2)}"))


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class SentenceField(QFrame):
    def __init__(self, sentence_field_name, sentence_field):
        super().__init__()

        sentence_layout = QHBoxLayout()
        sentence_layout.setAlignment(Qt.AlignLeft)

        font_style = QFont("Helvetica", 20)

        sentence_field_name_label = QLabel(sentence_field_name)
        sentence_field_name_label.setFont(font_style)
        sentence_field_name_label.setFixedWidth(200)
        sentence_field_name_label.setWordWrap(True)
        sentence_field_name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.sentence_field_label = QLabel(sentence_field)
        self.sentence_field_label.setFont(font_style)
        self.sentence_field_label.setAlignment(Qt.AlignCenter)
        self.sentence_field_label.setText("-")
        self.sentence_field_label.setFixedWidth(1400)
        self.sentence_field_label.setWordWrap(True)

        sentence_layout.addWidget(sentence_field_name_label)
        sentence_layout.addWidget(QVLine())
        sentence_layout.addWidget(self.sentence_field_label)

        self.setFixedHeight(100)
        self.setFrameStyle(QFrame.Plain | QFrame.Box)
        self.setLayout(sentence_layout)

    def set_label_text(self, text):
        self.sentence_field_label.setText(text)

class TableModel(QAbstractTableModel):
    def __init__(self, issue_names, data):
        super(TableModel, self).__init__()
        self._data = data
        self.issue_names = issue_names
        

    def data(self, index, role):
        if role == Qt.DisplayRole:
            item = self._data[index.row()][index.column()]
            return item[0]

        if role == Qt.ForegroundRole:
            item = self._data[index.row()][index.column()]
            return QColor(item[1])

        elif role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter | Qt.AlignVCenter)

        elif role == Qt.FontRole:
            if self._data[index.row()][index.column()][1] != "light gray" and self._data[index.row()][index.column()][1] != "black":
                return QFont("Helvetica", 20, QFont.Bold)
            return QFont("Helvetica", 20)

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self.issue_names[section] + ":"
        elif role == Qt.TextAlignmentRole:
            return int(Qt.AlignRight | Qt.AlignVCenter)
        elif role == Qt.FontRole:
            return QFont("Helvetica", 20, QFont.Bold)

        return super().headerData(section, orientation, role)

class OfferDetails(QTableView):
    def __init__(self, issue_names, data):
        super(OfferDetails, self).__init__()

        #font_style = QFont("Helvetica", 20)
        #self.setFont(font_style)
        #self.setAlignment(Qt.AlignCenter)
        #self.setText("Your Offer: ")
        #self.setStyleSheet("border: 1px solid black;")
        #self.setFixedHeight(100)
        #self.setFixedWidth(950)
        #self.setWordWrap(True)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        table_font = QFont('Arial', 24)
        self.setFont(table_font)
        self.offer_model = TableModel(issue_names, data)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setModel(self.offer_model)
        self.setFixedHeight(350)
        #self.setFixedWidth(950)

class UtilityCounter(QLabel):
    def __init__(self):
        super(UtilityCounter, self).__init__()

        font_style = QFont("Helvetica", 20)
        font_style.setBold(True)
        self.setFont(font_style)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Your Utility: \n - ")
        self.setStyleSheet("border: 1px solid black;")
        self.setFixedHeight(120)

class NegoStatus(QLabel):
    def __init__(self):
        super(NegoStatus, self).__init__()

        font_style = QFont("Helvetica", 20)
        self.setFont(font_style)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Caduceus is listening...")
        self.setStyleSheet("border: 1px solid black;")
        self.setFixedWidth(400)
        self.setFixedHeight(120)

class NegotiationGUI(QMainWindow):
    clean_gui = Signal()

    def __init__(self, screen, nego_time, robot_name):
        super().__init__()

        self.setWindowTitle("Human Robot Negotiation Interface")

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.layout = QGridLayout()
        self.layout.setSpacing(15)

        self.robot_name = robot_name

        self.layout.setRowStretch(5, 3)
        margin = QMargins()
        margin.setLeft(75)
        margin.setRight(75)
        margin.setTop(10)
        self.layout.setContentsMargins(margin)

        self.timer_widget = Timer(nego_time)
        self.human_sentence_widget = SentenceField("Your Offer ", "-")
        self.agent_sentence_widget = SentenceField(f"{self.robot_name}' Offer", "-")

        self.utility_counter = UtilityCounter()
        self.nego_status = NegoStatus()

        self.layout.addWidget(self.nego_status, 0, 0, 1, 1)
        self.layout.addWidget(self.timer_widget, 0, 1, 1, 1)
        self.layout.addWidget(self.utility_counter, 0, 2, 1, 1)

        self.layout.addWidget(self.human_sentence_widget, 1, 0, 1, 3)
        self.layout.addWidget(self.agent_sentence_widget, 2, 0, 1, 3)

        self.past_changes = [] 

        self.setScreen(screen)
        self.move(screen.geometry().topLeft())

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.clean_gui.connect(self.clean_up)

    def update_human_message(self, message):
        self.human_sentence_widget.set_label_text(str(message))

    def update_agent_message(self, message):
        self.agent_sentence_widget.set_label_text(str(message))

    def update_offer(self, message):
        self.offer_details_widget.setText(str(message))

    def update_offer_utility(self, message):    
        self.utility_counter.setText("Your Utility: \n" + str(message))

    def update_status(self, message):
        self.nego_status.setText(str(message))

    def create_table(self, issue_names, data):
        self.template_table = copy.deepcopy(data)
        self.data = copy.deepcopy(data)
        self.offer_details_widget = OfferDetails(issue_names, self.data)
        self.layout.addWidget(self.offer_details_widget, 3, 0, 2, 3)

    def clean_up(self):
        for i in self.__dict__:
            item = self.__dict__[i]
            clean(item)

        self.close()

    def reset_board(self):
        for x in range(len(self.data)):
            for y in range(len(self.data[x])):
                self.data[x][y] = (self.data[x][y][0], "black")
                self.offer_details_widget.model().dataChanged.emit(x, y)

    def update_grid_by_offer(self, changed_items):
        for x, y, value, color in changed_items:
            for sub_y in range(len(self.data[x])):
                self.data[x][sub_y] = (self.data[x][sub_y][0], "light gray")

            self.data[x][y] = (str(value).title(), color)
            self.offer_details_widget.model().dataChanged.emit(x, y)