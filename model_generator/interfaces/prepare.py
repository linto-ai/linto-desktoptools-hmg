#!/usr/bin/env python3
import os
import json
from random import shuffle
from shutil import copyfile

from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from base.project import Project
from base.dataset import DataSet
from interfaces.ui.prepare_ui import Ui_Prepare
from interfaces.ui.addsetdialog_ui import Ui_AddSetDialog

class Prepare(QtWidgets.QWidget):
    #TODO sample counter for validation is borked when checkbox are checked
    #TODO test validation on test and validation on test sub_set
    last_folder = "/home"
    prepare_complete = QtCore.pyqtSignal(name='prepare_complete')

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Prepare()
        self.ui.setupUi(self)
        self.project = project
        self.last_hotword_index = 0
        self.main_dataset = DataSet()
        # Init hotword list
        
        self.hotwords = self.project.project_info['hotwords']
        for hotword in self.hotwords:
            self.ui.current_hotword.addItem(hotword)

        self.sample_classes = [None] + self.hotwords

        # Init directory list
        self.folder_list_layout = QtWidgets.QVBoxLayout()
        self.folder_list = [[] for i in range(len(self.hotwords) + 1)]

        self.pie_slices = [QtChart.QPieSlice("non-hotword ()", 0)]
        self.pie_slices.extend([QtChart.QPieSlice("{} ()".format(name), 0) for name in self.hotwords])
        self.display_selected_directories(0)

        # Pie chart
        self.pie_series = QtChart.QPieSeries()
        for pie_slice in self.pie_slices:
            self.pie_series.append(pie_slice)
        self.pie_series.setHoleSize(0)

        self.pie_view = QtChart.QChartView()
        self.pie_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.pie_view.chart().layout().setContentsMargins(0,0,0,0)
        self.pie_view.chart().setMargins(QtCore.QMargins(0,0,0,0))
        self.pie_view.chart().legend().setAlignment(QtCore.Qt.AlignRight)
        self.pie_view.chart().addSeries(self.pie_series)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.pie_view)
        self.ui.graph_placeholder.setLayout(layout)

        #Connects
        self.ui.current_hotword.currentIndexChanged.connect(self.display_selected_directories)
        self.ui.add_folder_button.clicked.connect(self.add_folder)
        self.ui.test_subset_CB.stateChanged.connect(self.ui.test_subset_percent.setEnabled)
        self.ui.val_on_test_set_CB.stateChanged.connect(self.disable_validation_set)

        self.ui.training_percent.valueChanged.connect(self.on_trainsample_update)
        self.ui.validation_percent.valueChanged.connect(self.on_valsample_update)
        self.ui.test_percent.valueChanged.connect(self.on_testsample_update)
        self.ui.done_button.clicked.connect(self.on_done_clicked)
        self.ui.add_set_PB.clicked.connect(self.add_set)

    def display_selected_directories(self, index):
        self.ui.folder_list.clear()
        #TODO list is not cleared
        for folder in self.folder_list[index]:
            l_item = QtWidgets.QListWidgetItem()
            l_widget = Folder_Line(folder)
            l_widget.line_removed.connect(self.remove_folder)
            l_item.setSizeHint(l_widget.sizeHint())
            self.ui.folder_list.addItem(l_item)
            self.ui.folder_list.setItemWidget(l_item, l_widget)

    def update_hotword_combo_size(self, value):
        current_size = self.ui.current_hotword.count()
        if current_size > value + 1:
            self.ui.current_hotword.removeItem(current_size - 1)
        elif current_size < value + 1:
            self.ui.current_hotword.addItem("")
        self.update_hotword_combo_names()
    

    def remove_folder(self, folder):
        index = self.ui.current_hotword.currentIndex()
        self.folder_list[index].remove(folder)
        self.display_selected_directories(index)
        self.hotword_samples[index].setValue(self.hotword_samples[index].value() - len([f for f in os.listdir(folder) if f.endswith('.wav')]))
        self.update_sample_counter()
    
    def add_folder(self):
        index = self.ui.current_hotword.currentIndex()
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", self.last_folder)
        if len(res) != 0 and res not in self.folder_list[index]:
            self.last_folder = os.path.dirname(res)
            self.folder_list[index].append(res)
            self.display_selected_directories(index)
            self.main_dataset.add_from_folder(folder_path=res, 
                                              label = self.sample_classes[index],
                                              ext = ".wav")
            self.update_chart()

    def add_set(self):
        res = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file", self.last_folder, "Json file (*.json)")[0]
        if len(res) != 0:
            dialog = SetFilePreview(res)
            dialog.add_clicked.connect(self.main_dataset.add_from_manifest)
            dialog.exec()
            self.update_chart()

    def update_chart(self):
        total_sample = len(self.main_dataset)
        for i, hotword in enumerate(self.sample_classes):
            n_s = len(self.main_dataset.get_subset_by_label(hotword))
            self.pie_slices[i].setValue(n_s)
            if hotword is None:
                hotword = 'non-hotword'
            self.pie_slices[i].setLabel("{} : {} ({:.2f}%)".format(hotword, n_s, (0 if total_sample == 0 else n_s / total_sample * 100)))
            self.pie_view.chart().setTitle("{} samples".format(total_sample))

    def disable_validation_set(self, value:bool):
        self.ui.validation_percent.setValue(0.0)
        self.ui.test_percent.setValue(100 - self.ui.training_percent.value())
        self.ui.validation_percent.setEnabled(not value)
        self.ui.test_subset_percent.setValue(100.0)
        self.ui.test_subset_CB.setEnabled(value)
        self.ui.test_subset_CB.setChecked(False)
    
    def update_sets_sample_count(self):
        total_sample_count = len(self.main_dataset)
        self.ui.n_train_samples.setValue(round(total_sample_count * self.ui.training_percent.value() / 100))
        self.ui.n_test_samples.setValue(round(total_sample_count * self.ui.test_percent.value() / 100))
        if self.ui.val_on_test_set_CB.isChecked():
            self.ui.n_val_samples.setValue(self.ui.n_test_samples.value() * self.ui.test_subset_percent.value() / 100)
        else:
            self.ui.n_val_samples.setValue(round(total_sample_count * self.ui.validation_percent.value() / 100))
    
    def on_trainsample_update(self, value):
        total = sum([value, self.ui.validation_percent.value(), self.ui.test_percent.value()])
        if total > 100:
            self.ui.training_percent.setValue(value - (total - 100))
        self.update_sets_sample_count()
    
    def on_valsample_update(self, value):
        total = sum([self.ui.training_percent.value(), value, self.ui.test_percent.value()])
        if total > 100:
            self.ui.validation_percent.setValue(value - (total - 100))
        self.update_sets_sample_count()

    def on_testsample_update(self, value):
        total = sum([self.ui.training_percent.value(), self.ui.validation_percent.value(), value])
        if total > 100:
            self.ui.test_percent.setValue(value - (total - 100))
        self.update_sets_sample_count()

    def on_done_clicked(self):
        self.generate_sets()
        self.ui.folder_list.clear()

    def generate_sets(self):
        self.project.data_info['samples_location'] = dict()
        
        sub_set_by_label = []
        for hw in self.sample_classes:
            sub_set_by_label.append(self.main_dataset.get_subset_by_label(hw))
        
        train_set = DataSet()
        val_set = DataSet()
        test_set = DataSet()

        for s in sub_set_by_label:
            tr, val, test = s.split_dataset([self.ui.training_percent.value(), self.ui.validation_percent.value(), self.ui.test_percent.value()], not self.shuffle_set)
            train_set += tr
            val_set += val
            test_set += test
        for name, s in zip(["train", "val", "test"], [train_set, val_set, test_set]):
            json = os.path.join(self.project.project_location, "{}.json".format(name))
            self.project.data_info['{}_set'.format(name)] = json
            s.write(json) 
        
        self.project.data_info['set'] = True
        self.project.update_project()


    @property
    def training_percent(self):
        return self.ui.training_percent.value()
    
    @training_percent.setter
    def training_percent(self, value):
        self.ui.training_percent.setValue(value)

    @property
    def validation_percent(self):
        return self.ui.validation_percent.value()
    
    @validation_percent.setter
    def validation_percent(self, value):
        self.ui.validation_percent.setValue(value)

    @property
    def test_percent(self):
        return self.ui.test_percent.value()
    
    @test_percent.setter
    def test_percent(self, value):
        self.ui.test_percent.setValue(value)

    @property
    def shuffle_set(self):
        return self.ui.shuffle.isChecked()
    

def sorting_fun(item, separator, index):
    try:
        return item.split(separator)[index]
    except IndexError:
        return item
    
class Folder_Line(QtWidgets.QWidget):
    line_removed = QtCore.pyqtSignal(str, name='line_removed')
    
    def __init__(self, folder_name):
        super().__init__()
        self.folder_name = folder_name
        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(self.folder_name)
        button = QtWidgets.QPushButton("Remove")
        button.clicked.connect(self.removed)
        layout.addWidget(label)
        layout.addWidget(button)
        layout.addStretch()
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)

    def removed(self):
        self.line_removed.emit(self.folder_name)
        self.deleteLater()

class SetFilePreview(QtWidgets.QDialog):
    add_clicked = QtCore.pyqtSignal(str, list, list, list, name='add_clicked')
    def __init__(self, json_file):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_AddSetDialog()
        self.ui.setupUi(self)
        self.file = json_file
        try:
            with open(json_file, 'r') as f:
                self.manifest = json.load(f)
        except Exception as e:
            #TODO
            print("Error {}".format(str(e.args)))
            self.close()
        self.ui.samples_Label.setText("{} samples".format(len(self.manifest)))

        # Set Combox content
        keys = self.get_keys()
        self.ui.attr_key_CoB.addItem('None')
        for comboBox in [self.ui.file_key_CoB, self.ui.label_key_CoB, self.ui.attr_key_CoB]:
            for k in keys:
                comboBox.addItem(k)

        # connect 
        self.ui.add_PB.clicked.connect(self.on_add)
        self.ui.cancel_PB.clicked.connect(self.on_cancel)
    
    def get_keys(self):
        def recursive_search(dictionary, keys = [], prefix = None):
            for k in dictionary.keys():
                if type(dictionary[k]) is dict:
                    recursive_search(dictionary[k], keys, prefix="/".join([prefix, k]) if prefix is not None else k)
                else:
                    keys.append("/".join([prefix, k]) if prefix is not None else k)
            return keys
        sample = self.manifest[0]
        return recursive_search(self.manifest[0])
    
    def on_cancel(self):
        self.close()

    def on_add(self):
        self.add_clicked.emit(self.file,
                              self.ui.file_key_CoB.currentText().split("/"), 
                              self.ui.label_key_CoB.currentText().split("/"),
                              self.ui.attr_key_CoB.currentText().split("/"))
        self.close()