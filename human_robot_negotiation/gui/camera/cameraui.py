from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtGui import QAction, QBrush, QColor, QPalette
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, QStackedWidget, QWidget

class Ui_Camera(object):
    def setupUi(self, Camera):
        if not Camera.objectName():
            Camera.setObjectName(u"Camera")
        Camera.resize(668, 429)

        self.centralwidget = QWidget(Camera)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")

        self.viewfinderPage = QWidget()
        self.viewfinderPage.setObjectName(u"viewfinderPage")
        self.gridLayout_5 = QGridLayout(self.viewfinderPage)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.viewfinder = QVideoWidget(self.viewfinderPage)
        self.viewfinder.setObjectName(u"viewfinder")

        self.gridLayout_5.addWidget(self.viewfinder, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.viewfinderPage)

        self.gridLayout_3.addWidget(self.stackedWidget, 0, 0, 2, 1)

        Camera.setCentralWidget(self.centralwidget)

        self.stackedWidget.setCurrentIndex(0)

