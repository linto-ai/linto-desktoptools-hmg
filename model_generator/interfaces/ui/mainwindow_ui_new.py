# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 940)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.navBar = QtWidgets.QVBoxLayout()
        self.navBar.setSpacing(6)
        self.navBar.setObjectName("navBar")
        self.horizontalLayout.addLayout(self.navBar)
        self.line = QtWidgets.QFrame(self.centralWidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setObjectName("stackedWidget")
        self.mainStackedWidgetPage1 = QtWidgets.QWidget()
        self.mainStackedWidgetPage1.setObjectName("mainStackedWidgetPage1")
        self.stackedWidget.addWidget(self.mainStackedWidgetPage1)
        self.horizontalLayout.addWidget(self.stackedWidget)
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
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Hotword Model Generator (dev)"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOpen_Project.setTitle(_translate("MainWindow", "Open Project"))
        self.menu.setTitle(_translate("MainWindow", "?"))
        self.actionCreate_Project.setText(_translate("MainWindow", "Create Project"))
        self.actionClose_Project.setText(_translate("MainWindow", "Close Project"))
        self.action_open_other.setText(_translate("MainWindow", "Other ..."))
