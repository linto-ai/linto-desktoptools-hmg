# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'createDataset.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(446, 169)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.name_LE = QtWidgets.QLineEdit(Dialog)
        self.name_LE.setObjectName("name_LE")
        self.horizontalLayout_2.addWidget(self.name_LE)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.info_Label = QtWidgets.QLabel(Dialog)
        self.info_Label.setText("")
        self.info_Label.setObjectName("info_Label")
        self.verticalLayout.addWidget(self.info_Label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancel_PB = QtWidgets.QPushButton(Dialog)
        self.cancel_PB.setObjectName("cancel_PB")
        self.horizontalLayout.addWidget(self.cancel_PB)
        self.create_PB = QtWidgets.QPushButton(Dialog)
        self.create_PB.setObjectName("create_PB")
        self.horizontalLayout.addWidget(self.create_PB)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "New Dataset Name:"))
        self.cancel_PB.setText(_translate("Dialog", "Cancel"))
        self.create_PB.setText(_translate("Dialog", "Create DataSet"))
