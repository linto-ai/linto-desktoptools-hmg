#!/usr/bin/env python3
import os
import sys
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from base import Project
from interfaces.modules import _Module
from interfaces.ui.mainwindow_ui_new import Ui_MainWindow
from interfaces.navigation import Navigation
from interfaces.home import Home
from interfaces.utils.qtutils import create_vertical_spacer, empty_layout

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_project = Project()
        self.displayStatus("Welcome to HMG. To start: Open a project or Create a new project.")
        #self.populateNavbar()
        self.home = Home(self.current_project)
        self.home.project_openned.connect(self.onProjectOpenned)
        self.ui.stackedWidget.addWidget(self.home)
        self.ui.stackedWidget.setCurrentWidget(self.home)
        self.showMaximized()
    
    def displayStatus(self, message, timeout=0):
        self.ui.statusBar.showMessage(message, timeout)

    def createNavigation(self):
        self.navWidget = Navigation(self.current_project)
        self.navWidget.clicked.connect(self.switchTo)
        self.navPB = QtWidgets.QPushButton()
        play_icon = QtGui.QPixmap(os.path.join(DIR_PATH, "icons/home.png"))
        self.navPB.setIcon(QtGui.QIcon(play_icon))
        self.navPB.setIconSize(QtCore.QSize(50,50))
        self.navPB.setToolTip("Home")
        self.ui.stackedWidget.addWidget(self.navWidget)
        self.navPB.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.navWidget))
        self.ui.navBar.addWidget(self.navPB)
        self.ui.navBar.addItem(create_vertical_spacer())

    def onProjectOpenned(self, project: Project):
        self.clean()
        self.current_project = project
        self.createNavigation()
        self.displayStatus("Project openned: {}".format(project.project["name"]))

    def switchTo(self, interface: _Module):
        """
        Switch to given view.
        """
        if (interface not in self.ui.stackedWidget.children()):
            self.ui.stackedWidget.addWidget(interface)
            button = interface.icon()
            button.clicked.connect(lambda: self.switchTo(interface))
            self.ui.navBar.insertWidget(1, button)
            
        self.ui.stackedWidget.setCurrentWidget(interface)

    def clean(self):
        """
        Clear the side bar and the stackedWidget from all element.
        """
        empty_layout(self.ui.navBar.layout())
        empty_layout(self.ui.stackedWidget.layout())