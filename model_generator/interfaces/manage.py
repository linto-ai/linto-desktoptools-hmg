#!/usr/bin/env python3
import os
from shutil import copyfile
import json
from random import shuffle

from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from base.project import Project
from base.dataset import DataSet
from interfaces.ui.manage_ui import Ui_Manage
from interfaces.prepare import SetFilePreview

class Manage(QtWidgets.QWidget):
    datasets_modified = QtCore.pyqtSignal(name='datasets_modified')
    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Manage()
        self.ui.setupUi(self)
        self.project = project
        self.new_samples = DataSet()
        self.pie_view = None
        self.show_ratio(False)

        self.present_sets()
        self.init_comboBox()

        self.files = []
        #connect
        self.ui.add_PB.clicked.connect(self.add_samples)
        self.ui.browse_PB.clicked.connect(self.on_browse_clicked)
        self.ui.split_Radio.toggled.connect(self.show_ratio)
        self.ui.verify_PB.clicked.connect(self.verify)
        self.ui.addset_PB.clicked.connect(self.add_set)
        self.ui.clear_PB.clicked.connect(self.clear)

    def init_graph(self):
        self.pieSlices = []
        for hw in self.project.project_info['hotwords'] + ['non-hotword']:
            self.pieSlices.append(QtChart.QPieSlice("{} ()".format(hw), 0))
        self.pie_series = QtChart.QPieSeries()

        for pie_slice in self.pieSlices:
            self.pie_series.append(pie_slice)
        self.pie_series.setHoleSize(0)

        self.pie_view = QtChart.QChartView()
        self.pie_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.pie_view.chart().layout().setContentsMargins(0,0,0,0)
        self.pie_view.chart().setMargins(QtCore.QMargins(0,0,0,0))
        self.pie_view.chart().legend().setAlignment(QtCore.Qt.AlignBottom)
        self.pie_view.chart().addSeries(self.pie_series)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.pie_view)
        self.ui.graph_placeholder.setLayout(layout)

    def init_comboBox(self):
        for hw in self.project.project_info['hotwords'] + ['non-hotword']:
            self.ui.hotword_Combo.addItem(hw)

    def on_browse_clicked(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", "")
        if len(res) != 0:
            self.ui.browse_LE.setText(res)
            self.add_from_folder(res)
    
    def present_sets(self):
        self.ui.resume_TE.clear()
        if self.pie_view is None:
            self.init_graph()
        
        self.ui.resume_TE.appendPlainText("Data distribution\n")
        self.train_set = DataSet()
        self.train_set.load(self.project.data_info['train_set'])

        self.val_set = DataSet()
        self.val_set.load(self.project.data_info['val_set'])

        self.test_set = DataSet()
        self.test_set.load(self.project.data_info['test_set'])
        
        total_c = sum([len(s) for s in [self.train_set, self.val_set, self.test_set]])
        self.ui.resume_TE.appendPlainText("Total sample: {}\n".format(total_c))
        classes = self.project.project_info['hotwords'] + [None]
        class_count = [0 for _ in classes]

        for s, set_name in zip([self.train_set, self.val_set, self.test_set], ['Train', 'Validation', 'Test']):
            self.ui.resume_TE.appendPlainText('{} set : {} samples ({:.2f}%)\n'.format(set_name, len(s), (len(s)/ total_c *100) if total_c > 0 else 0.0))
            for i, cl in enumerate(classes):
                count = len(s.get_subset_by_label(cl))
                if cl is None :
                    cl = 'non-hotword'
                class_count[i] += count
                self.ui.resume_TE.appendPlainText('\t- {} : {} ({:.2f}%)\n'.format(cl, count, (count/len(s) * 100) if len(s) > 0 else 0))

        self.ui.resume_TE.appendPlainText('Total sample:\n'.format())
        for i, cl in enumerate(classes):
            class_name = classes[i]
            if class_name is None :
                class_name = 'non-hotword'
            self.ui.resume_TE.appendPlainText('\t- {} : {}({:.2f}%)'.format(class_name, class_count[i], (class_count[i] / total_c * 100) if total_c > 0 else 0))
            self.pieSlices[i].setValue(class_count[i])
            self.pieSlices[i].setLabel('{} : {}({:.2f}%)'.format(class_name, class_count[i], (class_count[i] / total_c * 100) if total_c > 0 else 0))

    def verify(self):
        missing_files = []
        for s, path in zip([self.train_set, self.val_set, self.test_set],
                           [self.project.data_info['train_set'], self.project.data_info['val_set'], self.project.data_info['test_set']]):
            missing_files.append(s.verify_and_clear())
            s.write(path)
        msgBox = QtWidgets.QMessageBox()
        if sum([len(l) for l in missing_files]) == 0:
            msgBox.setText("No missing file !")
        else:
            msgBox.setText("{} missing file (removed). \n Check terminal for details".format(sum([len(l) for l in missing_files])))
            for i, l in enumerate(missing_files):
                print("{} set : {} missing files".format(['Train', 'Validation', 'Test'][i], len(l)))
                for f in l:
                    print(f['file_path'])
        msgBox.exec()

    def clear(self):
        self.new_samples.clear()
        self.update_sample_preview()
        self.ui.clear_PB.setEnabled(False)
    
    def add_set(self, json_path):
        res = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file", "/home/", "Json file (*.json)")[0]
        if len(res) != 0:
            dialog = SetFilePreview(res)
            dialog.add_clicked.connect(self.new_samples.add_from_manifest)
            dialog.exec()
        self.update_sample_preview()

    def add_from_folder(self, folder):
        label = self.ui.hotword_Combo.currentText()
        if label == "non-hotword":
            label = None
        self.new_samples.add_from_folder(folder, label, ext='wav')
        self.update_sample_preview()

    
    def update_sample_preview(self):
        self.ui.samples_TE.clear()
        if len(self.new_samples) == 0:
            self.ui.samples_TE.appendPlainText("No samples")
            return
        self.ui.samples_TE.appendPlainText("New samples: {}\n".format(len(self.new_samples)))
        for hw in self.project.project_info['hotwords'] + [None]:
            self.ui.samples_TE.appendPlainText("\t{}: {} samples\n".format(hw if hw is not None else 'Non-hotword',len(self.new_samples.get_subset_by_label(hw))))
        if len(self.new_samples) > 0:
            self.ui.add_PB.setEnabled(True)
            self.ui.clear_PB.setEnabled(True)
        else:
            self.ui.add_PB.setEnabled(False)
            self.ui.clear_PB.setEnabled(False)

    def add_samples(self):
        split = False
        n_samples = len(self.new_samples)
        n_duplicate = 0
        if self.ui.train_Radio.isChecked():
            set_name = 'train_set'
        elif self.ui.test_Radio.isChecked():
            set_name = 'test_set'
        elif self.ui.val_Radio.isChecked():
            set_name = 'val_set'
        else:
            split = True
            set_name = ['train_set', 'test_set', 'val_set']
        
        if not split:
            #Add to a single set
            dataset = DataSet()
            dataset.load(self.project.data_info[set_name])
            dataset += self.new_samples
            if self.ui.duplicateCheck.isChecked():
                n_duplicate = dataset.remove_duplicate()
            dataset.write(self.project.data_info[set_name])
        else:
            #Add to multiple sets
            ratios = [self.ui.train_ratio.value(), self.ui.test_ratio.value(), self.ui.val_ratio.value()]
            if sum(ratios) == 0:
                QtWidgets.QMessageBox.warning(self, "No Ratio specified", "You must specify ratios")
                return
            else:
                dest = [DataSet() for _ in set_name]
                splits = self.new_samples.split_dataset(ratios, split_using_attr=True)
                for d, t, s in zip(dest, set_name, splits):
                    d.load(self.project.data_info[t])
                    d += s
                    if self.ui.duplicateCheck.isChecked():
                        n_duplicate = d.remove_duplicate()
                    d.write(self.project.data_info[t])
        

        QtWidgets.QMessageBox.warning(self, "Samples added", "Added {} samples ({} duplicates ignored)".format(n_samples - n_duplicate, n_duplicate)) 
            
        self.ui.add_PB.setEnabled(False)
        self.clear()
        self.present_sets()

    def show_ratio(self, visible):
        self.ui.val_ratio.setVisible(visible)
        self.ui.train_ratio.setVisible(visible)
        self.ui.test_ratio.setVisible(visible)