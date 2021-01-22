#!/usr/bin/env python3
import os
import sys
import threading
import json

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart, QtMultimedia


from base.dataset import DataSet
from scripts.audio_io import Player
from scripts.features import files2features
from scripts.keras_functions import load_keras, load_model
from interfaces.generate_test_set import TestSetDialog
from interfaces.progress_dialog import ProgressDialog
from interfaces.ui.test_ui import Ui_Test

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)
class Test(QtWidgets.QWidget):

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Test()
        self.ui.setupUi(self)
        self.project = project
        self.table_items = [] #Contain the confusion matrix items 
        self.init_conf_table()

        self.player = Player()

        #connects
        self.ui.test_button.clicked.connect(self.on_test_clicked)
        self.ui.browse_PB.clicked.connect(self.on_browse_clicked)
        self.ui.select_all_CB.toggled.connect(self.select_all)
        self.ui.exportTestSet_PB.clicked.connect(self.on_create_test_set)
        self.ui.external_CB.toggled.connect(self.external_test_set_changed)

    def init_conf_table(self):
        table = self.ui.conf_mat_table

        table.setRowCount(len(self.project.project_info['hotwords']) + 1) # +1 for non-hotword
        table.setColumnCount(len(self.project.project_info['hotwords']) + 1)
        table.setHorizontalHeaderLabels(['non-hotword'] + self.project.project_info['hotwords'])
        table.setVerticalHeaderLabels(['non-hotword'] + self.project.project_info['hotwords'])
        
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        for r in range(table.rowCount()):
            self.table_items.append([])
            for c in range(table.columnCount()):
                item = QtWidgets.QTableWidgetItem("")
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setData(0,0)
                self.table_items[r].append(item)
                table.setItem(r, c, item)

    def update_table(self):
        for r in self.table_items:
            for item in r:
                item.setText(str(item.data))
    
    def reset_table(self):
         for r in self.table_items:
            for item in r:
                item.setData(0,0)
    
    def reset_metrics(self):
        for i in reversed(range(self.ui.metric_GB.layout().count())):
            child = self.ui.metric_GB.layout().takeAt(i)
            if child.widget():
                child.widget().deleteLater()

    def on_test_clicked(self):
        self.setEnabled(False)
        self.reset_table()
        self.reset_metrics()
        self.model = load_model(self.project.model_path)
        print(self.model.summary())
        if self.ui.external_CB.isChecked():
            self.test_on_external()
        else:
            self.test_on_internal()
        self.setEnabled(True)

    def on_browse_clicked(self):
        res = QtWidgets.QFileDialog.getOpenFileName(self, "Select a testset file", "/home/", "Testset file (*.testset)")[0]
        if res is not None:
            self.ui.testSet_location_LE.setText(res)

    def display_metrics(self, result_matrix, n_samples):
        #Update table
        for row in range(result_matrix.shape[0]):
            for col in range(result_matrix.shape[1]):
                 self.table_items[row][col].setText(str(result_matrix[row][col]))

        #Display overall metrics
        self.ui.metric_layout.addLayout(self.gen_LabeledTextLine('Overall accuracy', np.sum(np.diag(result_matrix)), n_samples))
        self.ui.metric_layout.addLayout(self.gen_LabeledTextLine('False negative', np.sum(result_matrix[1:,0]), n_samples - np.sum(result_matrix[0])))
        self.ui.metric_layout.addLayout(self.gen_LabeledTextLine('False positive', n_samples - np.sum(np.diag(result_matrix)) - np.sum(result_matrix[1:,0]), n_samples))
        
        hotwords = self.project.project_info['hotwords']
        for i, hw in enumerate(hotwords):
            self.ui.metric_layout.addWidget(self.gen_HLine())
            self.ui.metric_layout.addWidget(QtWidgets.QLabel(hw))
            self.ui.metric_layout.addLayout(self.gen_LabeledTextLine('Accuracy', result_matrix[i+1, i+1], np.sum(result_matrix[i+1,:])))
            self.ui.metric_layout.addLayout(self.gen_LabeledTextLine('False Negative', np.sum(result_matrix[i+1,:]) - result_matrix[i+1, i+1], np.sum(result_matrix[i+1,:])))
            self.ui.metric_layout.addLayout(self.gen_LabeledTextLine('False Positive', np.sum(result_matrix[:,i+1]) - result_matrix[i+1, i+1], n_samples - np.sum(result_matrix[i+1,:])))
        
    def progress_display(self, value, goal, label):
        self.ui.progress_Label.setText(label)
        self.ui.progressBar.setValue(int(value/goal * 100))
        QtWidgets.QApplication.instance().processEvents()

    def test_on_internal(self):
        bad_results = []
        hotwords = self.project.project_info['hotwords']

        # Init outputs
        outputs = dict()
        outputs[None] = [0.0] * len(hotwords)
        for i, hw in enumerate(hotwords):
            outputs[hw] = [0.0] * len(hotwords)
            outputs[hw][i] = 1.0
        
        test_set = DataSet()
        test_set.load(self.project.data_info['test_set'])
        if self.ui.training_set.isChecked():
            test_set.load(self.project.data_info['train_set'])
        if self.ui.validation_set.isChecked():
            test_set.load(self.project.data_info['val_set'])


        # Extract features
        files, inputs, labels = files2features([s['file_path'] for s in test_set],
                                self.project.features_info,
                                labels=[outputs[s['label']] for s in test_set],
                                return_file=True,
                                progress_callback=self.progress_display)
        
        # Make prediction
        self.progress_display(1, 1, "Predicting ...")
        res = self.model.predict(inputs)

        self.progress_display(1, 1, "Processing results ...")
        # Result sorting
        result_matrix = np.zeros((len(hotwords) + 1, len(hotwords) + 1))
        for f, result, label in zip(files, res, labels):
            ct = np.argmax(label) + 1 if any(label) else 0 
            cp = np.squeeze(np.argwhere(result > self.threshold)) + 1 
            if cp.size == 0:
                cp = [0]
            elif cp.ndim == 0:
                cp = cp[np.newaxis]
            for c in cp:
                result_matrix[ct][c] += 1
                if c != ct:
                    bad_results.append((f, ct, c))
            
        self.progress_display(1, 1, "Done")
        
        # Display Metrics
        self.display_metrics(result_matrix, len(res))
        self.display_false_results(bad_results)

    def test_on_external(self):
        if self.ui.testSet_location_LE.text() == '':
            self.on_browse_clicked()
        if self.ui.testSet_location_LE.text() == '':
            return
        testset_manifest_path = self.ui.testSet_location_LE.text()
        testset_manifest_dir = os.path.dirname(testset_manifest_path)
        manifest = json.load(json.load(testset_manifest_path))

        # Set the order right
                    

    def select_all(self, val: bool):
        for widget in self.list_widgets:
            widget.CB.setChecked(val)
            
    def display_false_results(self, false_activations):
        self.ui.false_samples.clear()
        self.list_widgets = []
        for false_act in false_activations:
            l_item = QtWidgets.QListWidgetItem()
            l_widget = False_Activations(false_act, ['non-hotword'] + self.project.project_info['hotwords'], self.player)
            self.list_widgets.append(l_widget)
            l_item.setSizeHint(l_widget.sizeHint())
            self.ui.false_samples.addItem(l_item)
            self.ui.false_samples.setItemWidget(l_item, l_widget)

    def on_create_test_set(self):
        dialog = TestSetDialog(self, self.manifest)
        dialog.exec()
    
    def external_test_set_changed(self, ischecked):
        self.ui.training_set.setEnabled(not ischecked)
        self.ui.validation_set.setEnabled(not ischecked)
        self.ui.testSet_location_LE.setEnabled(ischecked)
        self.ui.browse_PB.setEnabled(ischecked)

    def gen_HLine(self):
        '''
        Generates and returns a Horizontal line
        ''' 
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line

    def gen_LabeledTextLine(self, label, value, total):
        layout = QtWidgets.QHBoxLayout()
        qlabel = QtWidgets.QLabel(label)
        lineEd = QtWidgets.QLineEdit("{}/{} ({:.4}%)".format(value, total, float(value)/total*100))
        lineEd.setReadOnly(True)
        layout.addWidget(qlabel)
        layout.addWidget(lineEd)
        return layout

    @property
    def threshold(self):
        return self.ui.threshold.value()
    
    @threshold.setter
    def threshold(self, value):
        self.ui.threshold.setValue(value)


class False_Activations(QtWidgets.QWidget):
    def __init__(self, result: tuple, labels: list, player: "Audio player"):
        super().__init__()
        self.file_path = result[0]
        self.sound = QtMultimedia.QSound(self.file_path)
        layout = QtWidgets.QHBoxLayout()
        self.CB = QtWidgets.QCheckBox(self.file_path)
        label = QtWidgets.QLabel("<font color='red'>{}</font> --> <font color='green'>{}</font>".format(labels[result[2]], labels[result[1]]))
        self.play_button = QtWidgets.QPushButton()
        play_icon = QtGui.QPixmap(os.path.join(DIR_PATH, "icons/play.png"))
        self.play_button.setIcon(QtGui.QIcon(play_icon))
        self.play_button.setIconSize(QtCore.QSize(20,20))
        layout.addWidget(self.CB)
        layout.addWidget(label)
        layout.addWidget(self.play_button)
        layout.addStretch()
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)

        self.play_button.clicked.connect(self.play_audio)

    def play_audio(self):
        self.sound.play()