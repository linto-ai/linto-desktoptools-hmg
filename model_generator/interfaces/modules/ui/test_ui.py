# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Test(object):
    def setupUi(self, Test):
        Test.setObjectName("Test")
        Test.resize(1867, 1113)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Test)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.profile_CB = QtWidgets.QComboBox(Test)
        self.profile_CB.setMinimumSize(QtCore.QSize(200, 0))
        self.profile_CB.setObjectName("profile_CB")
        self.horizontalLayout_3.addWidget(self.profile_CB)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.testSetGroup = QtWidgets.QGroupBox(Test)
        self.testSetGroup.setObjectName("testSetGroup")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.testSetGroup)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.testSetGroup)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.threshold = QtWidgets.QDoubleSpinBox(self.testSetGroup)
        self.threshold.setMinimum(0.01)
        self.threshold.setMaximum(1.0)
        self.threshold.setSingleStep(0.01)
        self.threshold.setProperty("value", 0.5)
        self.threshold.setObjectName("threshold")
        self.horizontalLayout.addWidget(self.threshold)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.training_set = QtWidgets.QCheckBox(self.testSetGroup)
        self.training_set.setObjectName("training_set")
        self.verticalLayout_2.addWidget(self.training_set)
        self.validation_set = QtWidgets.QCheckBox(self.testSetGroup)
        self.validation_set.setObjectName("validation_set")
        self.verticalLayout_2.addWidget(self.validation_set)
        self.line = QtWidgets.QFrame(self.testSetGroup)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.externalTest_group = QtWidgets.QHBoxLayout()
        self.externalTest_group.setObjectName("externalTest_group")
        self.external_CB = QtWidgets.QCheckBox(self.testSetGroup)
        self.external_CB.setObjectName("external_CB")
        self.externalTest_group.addWidget(self.external_CB)
        self.testSet_location_LE = QtWidgets.QLineEdit(self.testSetGroup)
        self.testSet_location_LE.setEnabled(False)
        self.testSet_location_LE.setObjectName("testSet_location_LE")
        self.externalTest_group.addWidget(self.testSet_location_LE)
        self.browse_PB = QtWidgets.QPushButton(self.testSetGroup)
        self.browse_PB.setEnabled(False)
        self.browse_PB.setObjectName("browse_PB")
        self.externalTest_group.addWidget(self.browse_PB)
        self.exportTestSet_PB = QtWidgets.QPushButton(self.testSetGroup)
        self.exportTestSet_PB.setEnabled(False)
        self.exportTestSet_PB.setObjectName("exportTestSet_PB")
        self.externalTest_group.addWidget(self.exportTestSet_PB)
        self.verticalLayout_2.addLayout(self.externalTest_group)
        self.verticalLayout_3.addWidget(self.testSetGroup)
        self.evaluate_PB = QtWidgets.QPushButton(Test)
        self.evaluate_PB.setObjectName("evaluate_PB")
        self.verticalLayout_3.addWidget(self.evaluate_PB)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(Test)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.conf_mat_table = QtWidgets.QTableWidget(Test)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.conf_mat_table.sizePolicy().hasHeightForWidth())
        self.conf_mat_table.setSizePolicy(sizePolicy)
        self.conf_mat_table.setObjectName("conf_mat_table")
        self.conf_mat_table.setColumnCount(0)
        self.conf_mat_table.setRowCount(0)
        self.verticalLayout.addWidget(self.conf_mat_table)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.metric_GB = QtWidgets.QGroupBox(Test)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.metric_GB.sizePolicy().hasHeightForWidth())
        self.metric_GB.setSizePolicy(sizePolicy)
        self.metric_GB.setObjectName("metric_GB")
        self.metric_layout = QtWidgets.QVBoxLayout(self.metric_GB)
        self.metric_layout.setContentsMargins(0, 0, 0, 0)
        self.metric_layout.setSpacing(0)
        self.metric_layout.setObjectName("metric_layout")
        self.horizontalLayout_2.addWidget(self.metric_GB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.select_all_CB = QtWidgets.QCheckBox(Test)
        self.select_all_CB.setText("")
        self.select_all_CB.setObjectName("select_all_CB")
        self.horizontalLayout_7.addWidget(self.select_all_CB)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.remove_PB = QtWidgets.QPushButton(Test)
        self.remove_PB.setObjectName("remove_PB")
        self.horizontalLayout_7.addWidget(self.remove_PB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.false_samples = QtWidgets.QListWidget(Test)
        self.false_samples.setObjectName("false_samples")
        self.verticalLayout_3.addWidget(self.false_samples)
        self.progress_Label = QtWidgets.QLabel(Test)
        self.progress_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_Label.setObjectName("progress_Label")
        self.verticalLayout_3.addWidget(self.progress_Label)
        self.progressBar = QtWidgets.QProgressBar(Test)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_3.addWidget(self.progressBar)

        self.retranslateUi(Test)
        QtCore.QMetaObject.connectSlotsByName(Test)

    def retranslateUi(self, Test):
        _translate = QtCore.QCoreApplication.translate
        Test.setWindowTitle(_translate("Test", "Form"))
        self.testSetGroup.setTitle(_translate("Test", "Test Set"))
        self.label.setText(_translate("Test", "Threshold"))
        self.training_set.setText(_translate("Test", "Include Training set"))
        self.validation_set.setText(_translate("Test", "Include validation set"))
        self.external_CB.setText(_translate("Test", "Use external Test Set"))
        self.browse_PB.setText(_translate("Test", "browse"))
        self.exportTestSet_PB.setText(_translate("Test", "Export test set"))
        self.evaluate_PB.setText(_translate("Test", "Evaluate"))
        self.label_2.setText(_translate("Test", "Confusion Matrix (Truth/Predicted)"))
        self.metric_GB.setTitle(_translate("Test", "Metrics"))
        self.remove_PB.setText(_translate("Test", "Remove Selected"))
        self.progress_Label.setText(_translate("Test", "Idle"))
