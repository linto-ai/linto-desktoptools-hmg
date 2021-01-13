#!/usr/bin/env python3
import os
import threading

import json
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from base.project import Project
from base.dataset import DataSet
from interfaces.ui.train_ui import Ui_Train
from scripts.keras_functions import load_keras, load_model, create_model, callbacks, Epoch_CallBack
from scripts.features import files2features


class Train(QtWidgets.QWidget):
    train_performed = QtCore.pyqtSignal(name='train_performed')
    model_deleted = QtCore.pyqtSignal(name='model_deleted')

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Train()
        self.ui.setupUi(self)
        self.project = project
        self.keras = load_keras()
        self.model = None
        self.current_epoch = 0
        self.vectorized = False # Indicate that samples features have already been extracted

        self.model_name = self.project.project_info['project_name'] + '.hdf5' if self.project.project_info['project_name'] != '' else 'model.hdf5'
        self.output_size = len(self.project.project_info['hotwords'])
        self.input_x, self.input_y = self.project.features_info['shape']
        self.init_graph()

        # Disable parameters already set
        if self.project.model_info['set']:
            self.current_epoch = self.project.model_info['epoch']
            self.set_parameter_enabled(False)
            self.ui.delete_PB.setEnabled(True)
            self.load_parameters()
            log_path = os.path.join(self.project.project_location, self.logfile_name())
            if os.path.isfile(log_path):
                self.load_training_log(log_path)
                self.update_graph_range()

            
        #Connect
        self.ui.epoch_train.toggled.connect(self.ui.progressBar.setVisible)
        self.ui.loss_fun.currentIndexChanged.connect(self.ui.loss_bias.setEnabled)
        self.ui.noise_CB.toggled.connect(self.ui.stdder.setEnabled)

        self.ui.train_button.clicked.connect(self.on_train_clicked)
        self.ui.stop_button.clicked.connect(self.on_stop_clicked)
        self.ui.delete_PB.clicked.connect(self.on_delete_clicked)
        self.ui.acc_stop_CB.stateChanged.connect(self.ui.acc_stop_value_SB.setEnabled)
        self.ui.dropout_CB.stateChanged.connect(self.ui.dropout.setEnabled)

    def data_set_updated(self):
        """ Called when dataset has been modified from an other tab"""
        self.vectorized = False

    def delete_model(self):
        """ Delete the model file and remove model and features info from manifest
        """
        if os.path.isfile(self.project.model_path):
            os.remove(self.project.model_path)
        
        if os.path.isfile(self.logfile_name()):
            os.remove(self.logfile_name())

        self.project.model_info = dict({'set': False})
        self.model = None

        self.ui.model_parameters.setEnabled(True)
        self.ui.delete_PB.setEnabled(False)
    
        self.project.update_project()

        self.current_epoch = 0

        self.text_output = "Idle"

        self.ui.progressBar.setValue(0)

    def init_graph(self):
        if self.ui.acc_graph_placeholder.layout() is None:
            acc_chart_Layout = QtWidgets.QVBoxLayout()
            loss_chart_Layout = QtWidgets.QVBoxLayout()
            self.ui.acc_graph_placeholder.setLayout(acc_chart_Layout)
            self.ui.loss_graph_placeholder.setLayout(loss_chart_Layout)

            acc_chart = QtChart.QChart()            
            loss_chart = QtChart.QChart()
            
            self.acc_chart_view = QtChart.QChartView(acc_chart)
            self.acc_chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
            
            self.loss_chart_view = QtChart.QChartView(loss_chart)
            self.loss_chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
            
            acc_chart_Layout.addWidget(self.acc_chart_view)
            loss_chart_Layout.addWidget(self.loss_chart_view)
            

            self.acc_chart_view.show()
            self.loss_chart_view.show()
            
        else:
            acc_chart = self.acc_chart_view.chart()
            loss_chart = self.loss_chart_view.chart()
            
        self.acc_serie = QtChart.QLineSeries()
        self.acc_serie.setName("train_acc")
        self.val_acc_serie = QtChart.QLineSeries()
        self.val_acc_serie.setName("val_acc")
        self.loss_serie = QtChart.QLineSeries()
        self.loss_serie.setName("loss")
        self.val_loss_serie = QtChart.QLineSeries()
        self.val_loss_serie.setName("val_loss")
        acc_chart.addSeries(self.acc_serie)
        acc_chart.addSeries(self.val_acc_serie)
        loss_chart.addSeries(self.loss_serie)
        loss_chart.addSeries(self.val_loss_serie)

        acc_chart.createDefaultAxes()
        loss_chart.createDefaultAxes()

        acc_chart.axisX().setRange(0, self.current_epoch)
        loss_chart.axisX().setRange(0, self.current_epoch)

    def load_parameters(self):
        for prop, key in zip([self.dropout, self.n_denses, self.dense_sizes, self.current_epoch],
                               ['dropout', 'dense_layers', 'dense_layer_sizes', 'epoch']):
            prop = self.project.model_info[key]

        self.ui.train_button.setText("Train (Current epoch = {})".format(self.current_epoch + 1))

    def load_training_log(self, log_path):
        """ Load training values from log file"""
        with open(log_path, "r") as f:
            for line in f.readlines():
                epoch, acc, val_acc, loss, val_loss = line.split()
                self.acc_serie.append(float(epoch), float(acc))
                self.val_acc_serie.append(float(epoch), float(val_acc))
                self.loss_serie.append(float(epoch), float(loss))
                self.val_loss_serie.append(int(epoch), float(val_loss))
        
        self.acc_serie.setName("train_acc ({:.5})".format(self.acc_serie.at(self.acc_serie.count() - 1).y()))
        self.val_acc_serie.setName("val_acc ({:.5})".format(self.val_acc_serie.at(self.val_acc_serie.count() - 1).y()))
        self.loss_serie.setName("loss ({:.5})".format(self.loss_serie.at(self.loss_serie.count() - 1).y()))
        self.val_loss_serie.setName("val_loss ({:.5})".format(self.val_loss_serie.at(self.val_loss_serie.count() - 1).y()))
        
        self.update_graph_range()

        self.acc_chart_view.update()
        self.loss_chart_view.update()

    def logfile_name(self):
        """ Generate logfile name based on modelpath"""
        return os.path.join(self.project.project_location, self.project.project_info['model_name'].split('.')[0] + '.log')

    def on_delete_clicked(self):
        ask_box = QtWidgets.QMessageBox(self)
        ask_box.setIcon(QtWidgets.QMessageBox.Question)
        ask_box.setText("Deleting the model is permanent and can't be reversed are you sure ?")
        ask_box.setWindowTitle("Delete model")
        ask_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        res = ask_box.exec()
        if res == QtWidgets.QMessageBox.Yes:
            self.delete_model()
            self.reset_graph()
            self.model_deleted.emit()
            self.ui.train_button.setText("Train (Current epoch = {})".format(self.current_epoch))

    def on_train_clicked(self):
        # UI updates
        self.ui.train_GB.setEnabled(False)
        self.ui.train_button.setEnabled(False)
        
        self.training()
        
        # UI updates
        self.ui.train_GB.setEnabled(True)
        self.set_parameter_enabled(False)
        self.ui.train_button.setText("Train (Current epoch = {})".format(self.current_epoch))
        self.ui.train_button.setEnabled(True)
        self.ui.delete_PB.setEnabled(True)
        self.project.model_info['set'] = True
        self.train_performed.emit()

    def on_stop_clicked(self):
        self.model.stop_training = True
        self.update_graph_range()
    
    def reset_graph(self):
        """ Remove values from series """
        self.acc_serie.clear()
        self.val_acc_serie.clear()
        self.loss_serie.clear()
        self.val_loss_serie.clear()

    def set_parameter_enabled(self, enabled):
        """ Enable/disable parameters groupbox """
        self.ui.model_parameters.setEnabled(enabled)

    def progress_display(self, value, goal, label):
        self.text_output = label
        self.ui.progressBar.setValue(int(value/goal * 100))
        QtWidgets.QApplication.instance().processEvents()
   
    def train_callback(self, epoch, logs = {}):
        """ Called during training at the end of each epoch"""
        self.progress_display(epoch, self.target_epoch, "Training (Epoch ={})...".format(epoch))
        self.acc_serie.append(epoch, logs['accuracy'])
        self.val_acc_serie.append(epoch, logs['val_accuracy'])
        self.val_loss_serie.append(epoch, logs['val_loss'])
        self.loss_serie.append(epoch, logs['loss'])
        self.current_epoch = epoch
        self.update_graph_range(self.target_epoch)

        self.acc_serie.setName("train_acc ({:.5})".format(logs['accuracy']))
        self.val_acc_serie.setName("val_acc ({:.5})".format(logs['val_accuracy']))
        self.loss_serie.setName("loss ({:.5})".format(logs['loss']))
        self.val_loss_serie.setName("val_loss ({:.5})".format(logs['val_loss']))

        self.acc_chart_view.update()
        self.loss_chart_view.update()

        if self.ui.acc_stop_CB.isChecked() and logs['val_accuracy'] >= self.ui.acc_stop_value_SB.value() / 100.:
            self.model.stop_training = True
            self.update_graph_range()

        QtWidgets.QApplication.instance().processEvents() # Refresh UI

    def training(self):
        """ Train the graph using paremeters set in the GUI """
        def check_dense_sizes(n_dense, dense_sizes):
            if len(dense_sizes) != n_dense:
                raise ValueError("The number of values for dense size must be equal to the number of dense layers.")

        # Load or create model
        if self.project.model_info['set']:
            if self.model == None:
                try:
                    self.model = load_model(self.project.model_path)
                except:
                    print("Could not load the model file at {}".format(self.project.model_path))
                    return
        else:
            try:
                check_dense_sizes(self.n_denses, self.dense_sizes)
            except ValueError as e:
                error_box = QtWidgets.QMessageBox(self)
                error_box.setIcon(QtWidgets.QMessageBox.Warning)
                error_box.setText(str(e.args))
                error_box.setWindowTitle("Error")
                error_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
                res = error_box.exec()
                
                return
            if self.model_name == '':
                self.ui.model_name.setFocus()
                return
            else:
                
                if not self.model_name.endswith('.hdf5'):
                    self.model_name = self.model_name + '.hdf5'
                self.project.project_info['model_name'] = self.model_name
            self.model = create_model(self.model_name, 
                                     (self.input_x, self.input_y),
                                     n_denses=self.n_denses,  
                                     dense_sizes=self.dense_sizes, 
                                     dropout=self.dropout, 
                                     output_size=self.output_size, 
                                     loss_fun=self.loss_bias, 
                                     #metrics=[], 
                                     noise_layer_derivation=self.gaussian_noise_stdder, 
                                     unroll=self.ui.unroll_CB.isChecked())

        self.callbacks = callbacks(os.path.join(self.project.project_location, self.project.project_info['model_name']), self.only_keep_best)

        self.callbacks.append(Epoch_CallBack(self.train_callback))
        self.target_epoch = self.current_epoch + self.n_epochs
        print(self.model.summary())  

        # Check and vectorize samples
        if not self.vectorized or self.ui.pos_only_CB.isChecked():
            self.validation_set, self.validation_set_output = [], []
            error_files = []
            hotwords = self.project.project_info['hotwords']

            train_dataset = DataSet()
            val_dataset = DataSet()

            train_dataset.load(self.project.data_info['train_set'])
            val_dataset.load(self.project.data_info['val_set'])

            # If train on keyword only is checked
            if self.ui.pos_only_CB.isChecked():
                train_dataset = train_dataset.get_subset_by_labels(self.project.project_info['hotwords'])
                val_dataset = val_dataset.get_subset_by_labels(self.project.project_info['hotwords'])

            outputs = dict()
            outputs[None] = [0.0] * len(hotwords)
            for i, hw in enumerate(hotwords):
                outputs[hw] = [0.0] * len(hotwords)
                outputs[hw][i] = 1.0
            self.progress_display(0, 1, "Collecting training samples ...")

            unproc_train = [(s['file_path'], outputs.get(s['label'], outputs[None])) for s in train_dataset]
            unproc_val = [(s['file_path'], outputs.get(s['label'], outputs[None])) for s in val_dataset]

            self.progress_display(0, 1, "Extracting training features ...")
            QtWidgets.QApplication.instance().processEvents()

            self.train_set, self.train_set_output = files2features([s[0] for s in unproc_train],
                                                                   self.project.features_info,
                                                                   labels=[s[1] for s in unproc_train], 
                                                                   progress_callback=self.progress_display)
            
            self.progress_display(0, 1, "Extracting validation features ...")

            self.validation_set, self.validation_set_output = files2features([s[0] for s in unproc_val],
                                                                             self.project.features_info,
                                                                             labels=[s[1] for s in unproc_val],
                                                                             progress_callback=self.progress_display)
                 
        self.progress_display(0, 1, "Training ...")
        self.ui.stop_button.setEnabled(True)
        QtWidgets.QApplication.instance().processEvents()
        
        # Fits model and uses outputs to update chart
        self.model.fit(self.train_set, 
                       self.train_set_output,
                       batch_size=self.batch_size,
                       initial_epoch=self.current_epoch,
                       epochs=self.target_epoch,
                       callbacks=self.callbacks,
                       validation_data=(self.validation_set,self.validation_set_output),
                       verbose=0,
                       shuffle=self.shuffle)

        self.ui.stop_button.setEnabled(False)
        self.text_output = "Training complete !"
        self.ui.progressBar.setValue(100)

        self.current_epoch += 1
        self.setup_model()
        self.write_training_log(self.logfile_name())
        
    def update_graph_range(self, x_max = None):
        # X range
        start_point = self.acc_serie.at(0).x() if self.acc_serie.count() > 0 else 0
        self.acc_chart_view.chart().axisX().setRange(start_point, self.current_epoch if x_max is None else x_max)
        self.loss_chart_view.chart().axisX().setRange(start_point, self.current_epoch if x_max is None else x_max)

        #Y range
        if self.acc_serie.count() > 0:
            loss_values = [self.loss_serie.at(i).y() for i in range(self.loss_serie.count())]
            loss_values.extend([self.val_loss_serie.at(i).y() for i in range(self.val_loss_serie.count())])
            max_loss = max([0,*loss_values])
            self.loss_chart_view.chart().axisY().setRange(0, max_loss)

            acc_values = [self.acc_serie.at(i).y() for i in range(self.acc_serie.count())]
            acc_values.extend([self.val_acc_serie.at(i).y() for i in range(self.val_acc_serie.count())])
            min_acc = min([1, *acc_values])
            self.acc_chart_view.chart().axisY().setRange(min_acc, 1)


    def setup_model(self):       

        #Write model parameters
        for key, value in zip(['input_shape', 'dropout', 'dense_layers', 'dense_layer_sizes', 'epoch'],
                              [self.project.features_info['shape'], self.dropout, self.n_denses, self.dense_sizes, self.current_epoch]):
            self.project.model_info[key] = value
        self.project.model_info['set'] = True
        self.project.update_project()

    def write_training_log(self, log_path):
        #TODO store values as binary
        acc = [str(self.acc_serie.at(i).y()) for i in range(self.acc_serie.count())]
        val_acc = [str(self.val_acc_serie.at(i).y()) for i in range(self.val_acc_serie.count())]
        loss = [str(self.loss_serie.at(i).y()) for i in range(self.loss_serie.count())]
        val_loss = [str(self.val_loss_serie.at(i).y()) for i in range(self.val_loss_serie.count())]
        with open(log_path, "w") as f:
            for i in range(len(acc)):
                f.write("{} {} {} {} {}\n".format(i, acc[i], val_acc[i], loss[i], val_loss[i]))

    @property
    def model_name(self) -> str:
        return self.ui.model_name.text()
    
    @model_name.setter
    def model_name(self, value):
        self.ui.model_name.setText(value)
    
    @property
    def input_x(self) -> int:
        return self.ui.input_x.value()
    
    @input_x.setter
    def input_x(self, value):
        self.ui.input_x.setValue(value)

    @property
    def input_y(self) -> int:
        return self.ui.input_y.value()
    
    @input_y.setter
    def input_y(self, value):
        self.ui.input_y.setValue(value)

    @property
    def output_size(self) -> int:
        return self.ui.output_size.value()
    
    @output_size.setter
    def output_size(self, value):
        self.ui.output_size.setValue(value)

    @property
    def dropout(self) -> float:
        return self.ui.dropout.value()
    
    @dropout.setter
    def dropout(self, value):
        self.ui.dropout.setValue(value) if self.ui.dropout_CB.isChecked() else 0

    @property
    def n_denses(self) -> int:
        return self.ui.n_layers.value()
        
    @n_denses.setter
    def n_denses(self, value: int):
        self.ui.n_layers.setValue(value)

    @property
    def dense_sizes(self) -> list:
        return [int(v) for v in self.ui.dense_size.text().strip().split(",")] if self.n_denses > 0 else []
    
    @dense_sizes.setter
    def dense_sizes(self, values:list):
        self.ui.dense_size.setText(", ".join([str(v) for v in values]))
    
    @property
    def use_epoch(self):
        return self.ui.epoch_train.isChecked()

    @use_epoch.setter
    def use_epoch(self, value: bool):
        self.ui.epoch_train.setChecked(value)
    
    @property
    def n_epochs(self) -> int:
        return self.ui.n_epochs.value()
    
    @n_epochs.setter
    def n_epochs(self, value):
        self.ui.n_epochs.setValue(value)

    @property
    def batch_size(self) -> int:
        return self.ui.batch_size.value()
    
    @batch_size.setter
    def batch_size(self, value):
        self.ui.batch_size.setValue(value)

    @property
    def loss_bias(self) -> float:
        return self.ui.loss_bias.value()
    
    @loss_bias.setter
    def loss_bias(self, value):
        self.ui.loss_bias.setValue(value)
    
    @property
    def shuffle(self):
        return self.ui.shuffle.isChecked()

    @shuffle.setter
    def shuffle(self, value: bool):
        self.ui.shuffle.setChecked(value)
    
    @property
    def only_keep_best(self):
        return self.ui.only_keep_best.isChecked()

    @only_keep_best.setter
    def only_keep_best(self, value: bool):
        self.ui.only_keep_best.setChecked(value)

    @property
    def text_output(self):
        return self.ui.output.text()

    @text_output.setter
    def text_output(self, value: str):
        self.ui.output.setText(value)
    
    @property
    def gaussian_noise_stdder(self):
        return self.ui.stdder if self.ui.noise_CB.isChecked() else None