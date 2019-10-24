# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 940)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_tab = QtWidgets.QTabWidget(self.centralWidget)
        self.main_tab.setEnabled(True)
        self.main_tab.setTabPosition(QtWidgets.QTabWidget.North)
        self.main_tab.setElideMode(QtCore.Qt.ElideRight)
        self.main_tab.setObjectName("main_tab")
        self.home = QtWidgets.QWidget()
        self.home.setObjectName("home")
        self.main_tab.addTab(self.home, "")
        self.verticalLayout.addWidget(self.main_tab)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1100, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuOpen_Project = QtWidgets.QMenu(self.menuFile)
        self.menuOpen_Project.setObjectName("menuOpen_Project")
        self.menu = QtWidgets.QMenu(self.menuBar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionCreate_Project = QtWidgets.QAction(MainWindow)
        self.actionCreate_Project.setObjectName("actionCreate_Project")
        self.actionClose_Project = QtWidgets.QAction(MainWindow)
        self.actionClose_Project.setObjectName("actionClose_Project")
        self.action_open_other = QtWidgets.QAction(MainWindow)
        self.action_open_other.setObjectName("action_open_other")
        self.menuOpen_Project.addSeparator()
        self.menuOpen_Project.addAction(self.action_open_other)
        self.menuOpen_Project.addSeparator()
        self.menuFile.addAction(self.actionCreate_Project)
        self.menuFile.addAction(self.menuOpen_Project.menuAction())
        self.menuFile.addAction(self.actionClose_Project)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.main_tab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Hotword Model Generator (dev)"))
        self.main_tab.setTabText(self.main_tab.indexOf(self.home), _translate("MainWindow", "Home"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOpen_Project.setTitle(_translate("MainWindow", "Open Project"))
        self.menu.setTitle(_translate("MainWindow", "?"))
        self.actionCreate_Project.setText(_translate("MainWindow", "Create Project"))
        self.actionClose_Project.setText(_translate("MainWindow", "Close Project"))
        self.action_open_other.setText(_translate("MainWindow", "Other ..."))

