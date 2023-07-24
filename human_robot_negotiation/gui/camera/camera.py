# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtMultimedia import QCamera, QCameraDevice, QImageCapture, QMediaCaptureSession, QMediaDevices
from PySide6.QtWidgets import QMainWindow, QMessageBox, QGridLayout, QStackedWidget, QWidget, QPushButton
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtCore import Qt
from PySide6.QtMultimediaWidgets import QVideoWidget

import cv2

from human_robot_negotiation.gui.camera.cameraui import Ui_Camera


class Camera(QMainWindow):
    def __init__(self, camera_callback):
        super().__init__()

        if not self.objectName():
            self.setObjectName(u"Camera")
        self.resize(668, 429)

        self.centralwidget = QWidget(self)
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
        self.setCentralWidget(self.centralwidget)

        self.stackedWidget.setCurrentIndex(0)

        self.m_devices = QMediaDevices()
        self.m_captureSession = QMediaCaptureSession()
        self.m_camera = None

        self.camera_index = len(QMediaDevices.videoInputs())-1 # get last camera

        # try to actually initialize camera & mic

        menu = self.menuBar()
        camera_menu = menu.addMenu("Cameras")
        camera_menu.triggered.connect(self.select_camera)
        
        for idx, camera in enumerate(QMediaDevices.videoInputs()):
            camera_action = QAction(QIcon(""), camera.description(), self)
            camera_action.setData(idx)
            camera_menu.addAction(camera_action)
            if "BRIO" in camera.description(): 
                self.camera_index = idx

        self.camera_callback = camera_callback
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.pressed.connect(self.confirm_func)
        self.gridLayout_5.addWidget(self.confirm_button, 1, 0)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

    def confirm_func(self):
        self.camera_callback(self.camera_index)

    def show(self):
        self.set_camera()
        super().show()
        
    def select_camera(self, act):
        self.stop_camera()
        self.camera_index = act.data()
        self.set_camera()

    def get_camera_index(self):
        return self.camera_index

    def set_camera(self):
        print("starting camera: ", self.camera_index)
        self.m_camera = QCamera(QMediaDevices.videoInputs()[self.camera_index])
        self.m_captureSession.setCamera(self.m_camera)
        self.m_camera.errorOccurred.connect(self.displayCameraError)
        self.m_captureSession.setVideoOutput(self.viewfinder)
        self.m_camera.start()
        
        print("cam error: ", self.m_camera.error())
        if self.m_camera.error() != QCamera.NoError:
            QMessageBox.warning(self, "Camera Error",
                                self.m_camera.errorString())

    def stop_camera(self):
        print("stopping camera: ", self.camera_index)
        self.m_camera.stop()

    def displayCameraError(self):
        if self.m_camera.error() != QCamera.NoError:
            QMessageBox.warning(self, "Camera Error",
                                self.m_camera.errorString())

    def closeEvent(self, event):
        self.stop_camera()