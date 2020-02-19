# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/hdd/repositories/qt/ui/export.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Export(object):
    def setupUi(self, Export):
        Export.setObjectName("Export")
        Export.resize(975, 550)
        self.verticalLayout = QtWidgets.QVBoxLayout(Export)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.manifest_PB = QtWidgets.QPushButton(Export)
        self.manifest_PB.setObjectName("manifest_PB")
        self.horizontalLayout_4.addWidget(self.manifest_PB)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tensorflow_PB = QtWidgets.QPushButton(Export)
        self.tensorflow_PB.setObjectName("tensorflow_PB")
        self.horizontalLayout_3.addWidget(self.tensorflow_PB)
        self.version_SB = QtWidgets.QSpinBox(Export)
        self.version_SB.setMinimum(1)
        self.version_SB.setObjectName("version_SB")
        self.horizontalLayout_3.addWidget(self.version_SB)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tensorflowJS_PB = QtWidgets.QPushButton(Export)
        self.tensorflowJS_PB.setEnabled(False)
        self.tensorflowJS_PB.setObjectName("tensorflowJS_PB")
        self.horizontalLayout_2.addWidget(self.tensorflowJS_PB)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.TFLite_PB = QtWidgets.QPushButton(Export)
        self.TFLite_PB.setEnabled(True)
        self.TFLite_PB.setObjectName("TFLite_PB")
        self.horizontalLayout_5.addWidget(self.TFLite_PB)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem4 = QtWidgets.QSpacerItem(20, 397, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)

        self.retranslateUi(Export)
        QtCore.QMetaObject.connectSlotsByName(Export)

    def retranslateUi(self, Export):
        _translate = QtCore.QCoreApplication.translate
        Export.setWindowTitle(_translate("Export", "Form"))
        self.manifest_PB.setToolTip(_translate("Export", "<html><head/><body><p>Generate manifest file describing model inputs, outputs and features parameters.</p></body></html>"))
        self.manifest_PB.setText(_translate("Export", "Generate Manifest"))
        self.tensorflow_PB.setToolTip(_translate("Export", "<html><head/><body><p>Generate tensorflow .pb (Protocol Buffer) model file.</p></body></html>"))
        self.tensorflow_PB.setText(_translate("Export", "Tensorflow format"))
        self.version_SB.setToolTip(_translate("Export", "model_version"))
        self.version_SB.setPrefix(_translate("Export", "v"))
        self.tensorflowJS_PB.setToolTip(_translate("Export", "Deactivated"))
        self.tensorflowJS_PB.setText(_translate("Export", "Tensorflow.JS format"))
        self.TFLite_PB.setToolTip(_translate("Export", "Deactivated"))
        self.TFLite_PB.setText(_translate("Export", "Tensoflow Lite format"))
