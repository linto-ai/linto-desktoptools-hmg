# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ui/generate_test_set.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 480)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.testsetname_LE = QtWidgets.QLineEdit(Dialog)
        self.testsetname_LE.setObjectName("testsetname_LE")
        self.horizontalLayout.addWidget(self.testsetname_LE)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.location_LE = QtWidgets.QLineEdit(Dialog)
        self.location_LE.setObjectName("location_LE")
        self.horizontalLayout_2.addWidget(self.location_LE)
        self.browse_PB = QtWidgets.QPushButton(Dialog)
        self.browse_PB.setObjectName("browse_PB")
        self.horizontalLayout_2.addWidget(self.browse_PB)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.data_desc_GB = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_desc_GB.sizePolicy().hasHeightForWidth())
        self.data_desc_GB.setSizePolicy(sizePolicy)
        self.data_desc_GB.setObjectName("data_desc_GB")
        self.verticalLayout_3.addWidget(self.data_desc_GB)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.cancel_PB = QtWidgets.QPushButton(Dialog)
        self.cancel_PB.setObjectName("cancel_PB")
        self.horizontalLayout_3.addWidget(self.cancel_PB)
        self.create_PB = QtWidgets.QPushButton(Dialog)
        self.create_PB.setObjectName("create_PB")
        self.horizontalLayout_3.addWidget(self.create_PB)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "TestSet Name:"))
        self.testsetname_LE.setPlaceholderText(_translate("Dialog", "mytestset"))
        self.label_2.setText(_translate("Dialog", "Location"))
        self.browse_PB.setText(_translate("Dialog", "Browse"))
        self.data_desc_GB.setTitle(_translate("Dialog", "Data"))
        self.cancel_PB.setText(_translate("Dialog", "Cancel"))
        self.create_PB.setText(_translate("Dialog", "Create TestSet"))

