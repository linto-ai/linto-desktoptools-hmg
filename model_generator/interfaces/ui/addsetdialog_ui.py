# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ui/addsetdialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddSetDialog(object):
    def setupUi(self, AddSetDialog):
        AddSetDialog.setObjectName("AddSetDialog")
        AddSetDialog.resize(473, 196)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddSetDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.samples_Label = QtWidgets.QLabel(AddSetDialog)
        self.samples_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.samples_Label.setObjectName("samples_Label")
        self.verticalLayout.addWidget(self.samples_Label)
        self.label_4 = QtWidgets.QLabel(AddSetDialog)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(AddSetDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.file_key_CoB = QtWidgets.QComboBox(AddSetDialog)
        self.file_key_CoB.setObjectName("file_key_CoB")
        self.horizontalLayout.addWidget(self.file_key_CoB)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(AddSetDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.label_key_CoB = QtWidgets.QComboBox(AddSetDialog)
        self.label_key_CoB.setObjectName("label_key_CoB")
        self.horizontalLayout_2.addWidget(self.label_key_CoB)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(AddSetDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.attr_key_CoB = QtWidgets.QComboBox(AddSetDialog)
        self.attr_key_CoB.setObjectName("attr_key_CoB")
        self.horizontalLayout_3.addWidget(self.attr_key_CoB)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.cancel_PB = QtWidgets.QPushButton(AddSetDialog)
        self.cancel_PB.setObjectName("cancel_PB")
        self.horizontalLayout_4.addWidget(self.cancel_PB)
        self.add_PB = QtWidgets.QPushButton(AddSetDialog)
        self.add_PB.setObjectName("add_PB")
        self.horizontalLayout_4.addWidget(self.add_PB)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(AddSetDialog)
        QtCore.QMetaObject.connectSlotsByName(AddSetDialog)

    def retranslateUi(self, AddSetDialog):
        _translate = QtCore.QCoreApplication.translate
        AddSetDialog.setWindowTitle(_translate("AddSetDialog", "Dialog"))
        self.samples_Label.setText(_translate("AddSetDialog", "TextLabel"))
        self.label_4.setText(_translate("AddSetDialog", "Select the proper keys:"))
        self.label.setText(_translate("AddSetDialog", "File Name Key"))
        self.label_2.setText(_translate("AddSetDialog", "Label Key"))
        self.label_3.setText(_translate("AddSetDialog", "Attribute Key"))
        self.cancel_PB.setText(_translate("AddSetDialog", "Cancel"))
        self.add_PB.setText(_translate("AddSetDialog", "Add Set"))

