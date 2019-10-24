#!/usr/bin/env python3
import os
import sys
import datetime
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from base.dataset import DataSet
from interfaces.ui.features_ui import Ui_Features
from interfaces.ui.features_chart_ui import Ui_Features_Charts
from interfaces.ui.mfcc_ui import Ui_MFCC
from scripts.qtutils import create_vertical_line, empty_layout

class Features(QtWidgets.QWidget):

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Features()
        self.ui.setupUi(self)
        self.project = project

        self.features_layout = QtWidgets.QHBoxLayout()

        self.current_feature = MFCC_Params()
        self.charts = FeaturesChart(self.project, self)
        self.ui.output_col_LCD.display(self.current_feature.output_size)
        self.features_layout.addWidget(self.current_feature)
        self.features_layout.addWidget(create_vertical_line())
        self.features_layout.addWidget(self.charts)
        self.ui.feature_Widget.setLayout(self.features_layout)
        self.ui.window_fun_CoB.setEnabled(self.current_feature.allow_window_fun)

        #connect
        self.current_feature.output_size_changed.connect(self.ui.output_col_LCD.display)
        self.ui.preEmp_CB.toggled.connect(self.ui.preEmp_SB.setEnabled)
        self.ui.sample_t.valueChanged.connect(self.update_row_value)
        self.ui.window_t_SP.valueChanged.connect(self.update_row_value)
        self.ui.stride_t_SB.valueChanged.connect(self.update_row_value)
        self.ui.setup_PB.clicked.connect(self.setup_features)
        self.ui.change_PB.clicked.connect(self.reset_features)
        self.ui.feature_CoB.currentIndexChanged.connect(self.feature_change)

        if self.project.features_info['set']:
            self.toggle_entries(False)

    def update_row_value(self, _):
        self.ui.output_row_LCD.display(self.row_size)

    def feature_change(self):
        #widgetToRemove = self.features_layout.itemAt(0).widget()
        #self.features_layout.removeWidget(self.current_feature)
        self.current_feature.deleteLater()
        self.features_layout.removeWidget(self.current_feature)
        feature_type = self.ui.feature_CoB.currentText()
        self.ui.feature_Widget.setLayout(self.features_layout)
        new_feature = {'mfcc':MFCC_Params, 'lmfe':LMFE_Params}[feature_type]
        self.current_feature = new_feature()
        self.features_layout.insertWidget(0,self.current_feature)


    def toggle_entries(self, enabled):
        for section in [self.ui.audio_parameters, self.ui.preprocess, self.ui.windows, self.current_feature, ]:
            section.setEnabled(enabled)
        self.ui.setup_PB.setEnabled(enabled)
        self.ui.change_PB.setEnabled(not enabled)

    def setup_features(self):
        self.project.features_info = self.generate_dict()
        self.project.update_project()
        self.toggle_entries(False)

    def generate_dict(self):
        parameters = dict()
        for key, value in zip(['shape', 'sample_rate', 'encoding', 'sample_t', 'window_t', 'hop_t', 'emphasis'],
                              [[self.row_size, self.current_feature.output_size], self.sample_rate, self.encoding, self.sample_t, self.window_t, self.hop_t, self.preEmp]):
            parameters[key] = value
        parameters['features_param'] = self.current_feature.features_params()
        parameters['set'] = True
        return parameters

    def reset_features(self):
        # Add Dialog
        self.project.features_info ={'set' : False}
        self.project.update_project()
        self.toggle_entries(True)

    @property
    def sample_rate(self):
        return self.ui.sample_rate.value()

    @property
    def encoding(self):
        return self.ui.encoding.value()
    
    @property
    def sample_t(self):
        return self.ui.sample_t.value()
    
    @property
    def preEmp(self):
        return self.ui.preEmp_SB.value() if self.ui.preEmp_CB.isChecked() else None

    @property
    def window_t(self):
        return self.ui.window_t_SP.value()

    @property
    def hop_t(self):
        return self.ui.stride_t_SB.value()

    @property
    def row_size(self):
        return int((self.sample_t - self.window_t)/self.hop_t) + 1
    
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scripts.features import files2features
import numpy as np
class FeaturesChart(QtWidgets.QWidget):
    def __init__(self, project, tab):
        super().__init__()
        self.ui = Ui_Features_Charts()
        self.ui.setupUi(self)
        self.project = project
        self.tab = tab
        self.layout = QtWidgets.QVBoxLayout()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ui.chart_Widget.setLayout(self.layout)
        #connect
        self.ui.analyse_PB.clicked.connect(self.generate_charts)

    def generate_charts(self):
        empty_layout(self.layout)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        base_text = self.ui.analyse_PB.text()
        self.ui.analyse_PB.setText("Processing ...")

        hotwords = self.project.project_info['hotwords']
        n_graph = 1 + self.ui.variance_CB.isChecked()
        dataset = DataSet()
        dataset.load(self.project.data_info['train_set'])
        for i, hotword in enumerate(hotwords):
            axes = self.figure.add_subplot(len(hotwords),n_graph,i*n_graph + 1)
            axes.clear()
            files = [sample['file_path'] for sample in dataset.get_subset_by_label(hotword)]
            data = files2features(files, self.tab.generate_dict())
            axes.imshow(np.mean(data, axis=0).T, interpolation='nearest', origin='lower')
            axes.set_title("{} (mean)".format(hotword))
            
            if self.ui.variance_CB.isChecked():
                axes = self.figure.add_subplot(len(hotwords),n_graph,i*n_graph + 2)
                axes.clear()
                
                axes.imshow(np.var(data, axis=0).T, interpolation='nearest', origin='lower')
                axes.set_title("{} (variance)".format(hotword))
        
        self.canvas.draw()
        self.ui.analyse_PB.setText(base_text)

    def process_samples(self, hotword):
        pass

    def clear_charts(self):
        pass



class MFCC_Params(QtWidgets.QWidget):
    feature_name = 'mfcc'
    allow_window_fun = False
    output_size_changed = QtCore.pyqtSignal(int, name='output_size_changed')
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MFCC()
        self.ui.setupUi(self)

        # connect
        self.ui.ncoef_SP.valueChanged.connect(self.size_changed)
        self.ui.nfilt_SP.valueChanged.connect(self.check_value)
    
    def check_value(self, value):
        self.n_filt = value

    def size_changed(self, value):
        self.output_size_changed.emit(self.output_size)
        self.n_coef = value

    def features_params(self):
        params = dict()
        params['feature_type'] = self.feature_name
        params['n_fft'] = self.fft_size
        params['n_filt'] = self.n_filt
        params['n_coef'] = self.n_coef
        params['energy'] = self.use_energy
        return params

    @property
    def fft_size(self) -> int:
        return self.ui.nfft_SP.value()

    @property
    def n_filt(self) -> int:
        return self.ui.nfilt_SP.value()

    @n_filt.setter
    def n_filt(self, value):
        self.ui.nfilt_SP.setValue(value)
        if self.n_coef > self.n_filt:
            self.n_coef = self.n_filt
    @property
    def n_coef(self) -> int:
        return self.ui.ncoef_SP.value()
    
    @n_coef.setter
    def n_coef(self, value):
        self.ui.ncoef_SP.setValue(value)
        if self.n_coef > self.n_filt:
            self.n_coef = self.n_filt

    @property
    def output_size(self) -> int:
        return self.n_coef

    @property
    def use_energy(self) -> bool:
        return self.ui.use_energy_CB.isChecked()

class LMFE_Params(MFCC_Params):
    feature_name = 'lmfe'
    def __init__(self):
        MFCC_Params.__init__(self)
        self.ui = Ui_MFCC()
        self.ui.setupUi(self)