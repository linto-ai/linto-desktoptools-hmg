# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addFromFolder.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(560, 368)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.browse_LE = QtWidgets.QLineEdit(Dialog)
        self.browse_LE.setEnabled(False)
        self.browse_LE.setObjectName("browse_LE")
        self.horizontalLayout_2.addWidget(self.browse_LE)
        self.browse_PB = QtWidgets.QPushButton(Dialog)
        self.browse_PB.setObjectName("browse_PB")
        self.horizontalLayout_2.addWidget(self.browse_PB)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.duplicate_CB = QtWidgets.QCheckBox(Dialog)
        self.duplicate_CB.setObjectName("duplicate_CB")
        self.horizontalLayout_3.addWidget(self.duplicate_CB)
        self.recurs_CB = QtWidgets.QCheckBox(Dialog)
        self.recurs_CB.setObjectName("recurs_CB")
        self.horizontalLayout_3.addWidget(self.recurs_CB)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.output_TE = QtWidgets.QPlainTextEdit(Dialog)
        self.output_TE.setObjectName("output_TE")
        self.verticalLayout.addWidget(self.output_TE)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.keyword_CB = QtWidgets.QComboBox(Dialog)
        self.keyword_CB.setCurrentText("")
        self.keyword_CB.setObjectName("keyword_CB")
        self.horizontalLayout_4.addWidget(self.keyword_CB)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cancel_PB = QtWidgets.QPushButton(Dialog)
        self.cancel_PB.setObjectName("cancel_PB")
        self.horizontalLayout.addWidget(self.cancel_PB)
        self.add_PB = QtWidgets.QPushButton(Dialog)
        self.add_PB.setObjectName("add_PB")
        self.horizontalLayout.addWidget(self.add_PB)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.browse_PB.setText(_translate("Dialog", "Browse"))
        self.duplicate_CB.setToolTip(_translate("Dialog", "<html><head/><body><p>If checked, will ignore files with the same name during search.</p></body></html>"))
        self.duplicate_CB.setText(_translate("Dialog", "Remove duplicates"))
        self.recurs_CB.setToolTip(_translate("Dialog", "<html><head/><body><p>If checked will include subfolder search.</p></body></html>"))
        self.recurs_CB.setText(_translate("Dialog", "Recursive search"))
        self.label.setText(_translate("Dialog", "Add To :"))
        self.cancel_PB.setText(_translate("Dialog", "Cancel"))
        self.add_PB.setText(_translate("Dialog", "Add Samples"))
