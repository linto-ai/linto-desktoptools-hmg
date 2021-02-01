# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/hdd/repositories/qt/ui/mfcc.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MFCC(object):
    def setupUi(self, MFCC):
        MFCC.setObjectName("MFCC")
        MFCC.resize(374, 306)
        self.verticalLayout = QtWidgets.QVBoxLayout(MFCC)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(MFCC)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.nfft_SP = QtWidgets.QSpinBox(MFCC)
        self.nfft_SP.setMaximum(16000)
        self.nfft_SP.setProperty("value", 512)
        self.nfft_SP.setObjectName("nfft_SP")
        self.horizontalLayout.addWidget(self.nfft_SP)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(MFCC)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.nfilt_SP = QtWidgets.QSpinBox(MFCC)
        self.nfilt_SP.setMinimum(1)
        self.nfilt_SP.setProperty("value", 20)
        self.nfilt_SP.setObjectName("nfilt_SP")
        self.horizontalLayout_2.addWidget(self.nfilt_SP)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(MFCC)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.ncoef_SP = QtWidgets.QSpinBox(MFCC)
        self.ncoef_SP.setMinimum(1)
        self.ncoef_SP.setMaximum(40)
        self.ncoef_SP.setProperty("value", 13)
        self.ncoef_SP.setObjectName("ncoef_SP")
        self.horizontalLayout_3.addWidget(self.ncoef_SP)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.use_energy_CB = QtWidgets.QCheckBox(MFCC)
        self.use_energy_CB.setObjectName("use_energy_CB")
        self.verticalLayout.addWidget(self.use_energy_CB)
        spacerItem = QtWidgets.QSpacerItem(20, 183, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(MFCC)
        QtCore.QMetaObject.connectSlotsByName(MFCC)

    def retranslateUi(self, MFCC):
        _translate = QtCore.QCoreApplication.translate
        MFCC.setWindowTitle(_translate("MFCC", "Form"))
        self.label.setText(_translate("MFCC", "FFT SIze"))
        self.label_2.setText(_translate("MFCC", "Num Filters"))
        self.label_3.setText(_translate("MFCC", "Num Coeff"))
        self.use_energy_CB.setText(_translate("MFCC", "Use Log Energy"))
