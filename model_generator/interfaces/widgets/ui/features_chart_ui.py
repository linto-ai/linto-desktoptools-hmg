# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ui/features_charts.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Features_Charts(object):
    def setupUi(self, Features_Charts):
        Features_Charts.setObjectName("Features_Charts")
        Features_Charts.resize(687, 526)
        self.verticalLayout = QtWidgets.QVBoxLayout(Features_Charts)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.variance_CB = QtWidgets.QCheckBox(Features_Charts)
        self.variance_CB.setObjectName("variance_CB")
        self.horizontalLayout.addWidget(self.variance_CB)
        self.analyse_PB = QtWidgets.QPushButton(Features_Charts)
        self.analyse_PB.setObjectName("analyse_PB")
        self.horizontalLayout.addWidget(self.analyse_PB)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(Features_Charts)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.chart_Widget = QtWidgets.QWidget(Features_Charts)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chart_Widget.sizePolicy().hasHeightForWidth())
        self.chart_Widget.setSizePolicy(sizePolicy)
        self.chart_Widget.setObjectName("chart_Widget")
        self.verticalLayout.addWidget(self.chart_Widget)

        self.retranslateUi(Features_Charts)
        QtCore.QMetaObject.connectSlotsByName(Features_Charts)

    def retranslateUi(self, Features_Charts):
        _translate = QtCore.QCoreApplication.translate
        Features_Charts.setWindowTitle(_translate("Features_Charts", "Form"))
        self.variance_CB.setText(_translate("Features_Charts", "Display Variance"))
        self.analyse_PB.setText(_translate("Features_Charts", "Analyse samples"))

