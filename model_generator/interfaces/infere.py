#!/usr/bin/env python3
import os
import sys
import json
from collections import deque
from threading import Thread

import numpy as np

from sonopy import mfcc_spec
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from scripts.inference import PredictFun
from scripts.audio_io import Player
from scripts.features import signal2features
from scripts.signal_processing import pre_emphasis
from scripts.keras_functions import load_model
from interfaces.ui.infere_ui import Ui_Infere
from interfaces.addtoset import AddToSet

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)
GRAPH_RANGE = 120
INFERENCE_STEP = 200 #ms
class Infere(QtWidgets.QWidget):
    activation_spotted = QtCore.pyqtSignal(bytes, str, name='activation_spotted')

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.ui = Ui_Infere()
        self.ui.setupUi(self)
        
        #Set icon to delete button
        cancel_icon = QtGui.QPixmap(os.path.join(DIR_PATH, "icons/cancel.png"))
        self.ui.delete_PB.setIcon(QtGui.QIcon(cancel_icon))
        self.ui.delete_PB.setIconSize(QtCore.QSize(20,20))

        self.audio = None
        self.buffer = [] # Contains signal 
        self.feat_buffer = np.zeros((30,13)).tolist() # Contains features
        self.running = False
        self.wait = False

        #Graph
        self.init_graph()

        #Audio player
        self.player = Player()

        #Connects
        self.ui.threshold.valueChanged.connect(self.on_threshold_changed)
        self.ui.test_pb.clicked.connect(self.on_test_clicked)
        self.activation_spotted.connect(self.add_activated_sample)
        self.ui.checkAll.toggled.connect(self.check_all)
        self.ui.delete_PB.clicked.connect(self.delete_all)
        self.ui.add_to_set_PB.clicked.connect(self.add_to_sets)

          
    def on_test_clicked(self):
        audio_params = self.project.features_info
        features_params = audio_params['features_param']
        

        if not self.audio:
            self.init_audio_input()
            self.feature_fun = lambda x : signal2features(x, audio_params,features_params)
            self.init_inference_engine()
        if not self.running: # start
            for serie in self.series:
                serie.clear()
            self.ui.activation_list.setEnabled(False)
            self.buffer = [] #Contains normalized audio input
            self.current_buffer = [] #Contains raw audio being infered
            self.text_output = "..."
            self.stream.start_stream()
            self.th = Thread(target=self.run, args=())
            self.th.start()
            self.test_button = "Stop"
        else: # stop
            self.running = False
            self.th.join()
            self.stream.stop_stream()
            self.test_button = "Test"
            self.text_output = 'Waiting ...'
            self.ui.activation_list.setEnabled(True)

    def init_graph(self):
        graph_layout = QtWidgets.QHBoxLayout()
        self.ui.graph_placeholder.setLayout(graph_layout)

        # Prediction chart
        self.chart = QtChart.QChart()
        self.chart_view = QtChart.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        graph_layout.addWidget(self.chart_view)

        self.threshold_serie = QtChart.QLineSeries()
        self.threshold_serie.setName("threshold")
        self.threshold_serie.setPen(QtGui.QPen(QtGui.QColor("black")))
        self.threshold_serie.append(-GRAPH_RANGE, self.threshold)
        self.threshold_serie.append(9001, self.threshold)
        self.chart.addSeries(self.threshold_serie)

        self.series = [QtChart.QLineSeries() for _ in range(len(self.project.project_info['hotwords']))]
        for serie, label in zip(self.series, self.project.project_info['hotwords']):
            serie.setName(label)        
            self.chart.addSeries(serie)
        self.chart.createDefaultAxes()
        self.chart.axisY().setRange(0,1)

    def update_output(self, values):
        for serie, v in zip(self.series, values):
            serie.append(self.series[0].count() * self.project.features_info['hop_t'], v)        

        self.chart.axisX().setRange((self.series[0].count()  - GRAPH_RANGE) * self.project.features_info['hop_t'], self.series[0].count() * self.project.features_info['hop_t'])
        self.chart_view.update()
        QtWidgets.QApplication.instance().processEvents()

    def init_audio_input(self):
        import pyaudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.hop_s)
    
    def on_threshold_changed(self, value):
        self.threshold_serie.clear()
        self.threshold_serie.append(-GRAPH_RANGE, self.threshold)
        self.threshold_serie.append(9001, self.threshold)
        
    def init_inference_engine(self):
        self.kws = PredictFun(self.project.model_path)

    def run(self):
        self.running = True
        waiting_frames = int(self.sample_rate * self.project.features_info['sample_t'] / self.hop_s)
        last_value = None
        cp = -1
        current_buffer = bytes([0] * self.audio_sample_size)  
        reading_step = int(self.sample_rate * INFERENCE_STEP * 0.001)
        feature_length = self.project.model_info['input_shape'][0]
        net_input = []
        while self.running:
            raw_buffer = self.stream.read(reading_step, exception_on_overflow=False)
            current_buffer += raw_buffer
            
            new_data = np.frombuffer(raw_buffer, dtype='<i2').astype(np.float32, order='C') / 32767.0
            # Apply pre-emphasis if set
            if 'emphasis' in self.project.features_info and self.project.features_info['emphasis'] is not None:
                new_data = pre_emphasis(new_data, self.project.features_info['emphasis'], previous_value=last_value)
                last_value = new_data[-1]

            self.buffer.extend(new_data)
            
            if len(self.buffer) >= self.window_s:
                # Extract features
                feats = self.feature_fun(self.buffer)
                self.feat_buffer.extend(feats)
                self.buffer = self.buffer[len(feats)* self.hop_s:]
            else:
                continue
            
            # Net inputs
            net_input = np.zeros((len(feats) + 1, feature_length, self.project.model_info['input_shape'][1]))
            for i in range(len(self.feat_buffer) - feature_length + 1):
                net_input[i] = self.feat_buffer[i:i+feature_length]
            
            self.feat_buffer = self.feat_buffer[len(feats):]
            
            # Infere
            res = self.kws.predict(net_input)

            # Processing results
            for i, r in enumerate(res):
                self.update_output(r)
                
                # Waiting frames
                if self.wait:
                    self.wait -= 1
                    if not self.wait:
                        self.text_output = '...'
                    continue

                # Thresholds
                res_th = (r > self.threshold).astype(int)
                if not res_th.any(): #silence
                    continue
                
                # Detection
                self.wait = waiting_frames
                cp = np.argmax(r)
                self.activation_spotted.emit(current_buffer[-self.audio_sample_size:], self.project.project_info['hotwords'][cp])
                self.text_output = self.project.project_info['hotwords'][cp]
                
                # Cleaning
            offset = len(raw_buffer)
            current_buffer = current_buffer[offset:]
            print("{:6}".format(len(current_buffer)), end='\r', flush=True)
                

        print("stream stopped")

    def add_activated_sample(self, data: "Audio data", label: "Activated class"):
        l_item = QtWidgets.QListWidgetItem()
        l_widget = Activation_Sample(data, label, ['non-hotword'] + self.project.project_info['hotwords'], self.player, l_item)
        l_widget.deleted.connect(self.delete_sample)
        l_item.setSizeHint(l_widget.sizeHint())
        
        self.ui.activation_list.addItem(l_item)
        self.ui.activation_list.setItemWidget(l_item, l_widget)

    def delete_sample(self, list_item):
        self.ui.activation_list.takeItem(self.ui.activation_list.row(list_item))

    def stop_thread(self):
        #Call when the window is closed
        self.running = False
        self.th.join()

    def check_all(self, val):
        for i in range(self.ui.activation_list.count()):
            item = self.ui.activation_list.item(i)
            widget = self.ui.activation_list.itemWidget(item)
            widget.CB.setChecked(val)

    def delete_all(self):
        delete_list = []
        for i in range(self.ui.activation_list.count()):
            item = self.ui.activation_list.item(i)
            widget = self.ui.activation_list.itemWidget(item)
            if widget.CB.isChecked():
                delete_list.append(i)
        delete_list.reverse()
        for i in delete_list:
            self.ui.activation_list.takeItem(i)

    def get_samples(self):
        ''' Returns samples if checkbox is checked.
        Return format is [(label, data)]
        '''
        samples = []
        for i in range(self.ui.activation_list.count()):
            item = self.ui.activation_list.item(i)
            widget = self.ui.activation_list.itemWidget(item)
            if not widget.CB.isChecked():
                continue
            samples.append((widget.hotword_CB.currentText(), widget.data))
        return samples

    def add_to_sets(self):
        dialog = AddToSet(self, self.manifest, self.manifest_path, self.get_samples())
        dialog.samples_added.connect(self.delete_all)
        dialog.show()

    @property
    def sample_rate(self):
        """ Audio sampling rate """
        return self.project.features_info['sample_rate']

    @property
    def hop_s(self):
        return int(self.project.features_info['hop_t'] * self.sample_rate)

    @property
    def window_s(self):
        return int(self.project.features_info['window_t'] * self.sample_rate)
    
    @property
    def test_button(self):
        return self.ui.test_pb.text()

    @test_button.setter
    def test_button(self, text):
        self.ui.test_pb.setText(text) 

    @property
    def threshold(self):
        return self.ui.threshold.value()

    @threshold.setter
    def threshold(self, value):
        self.ui.threshold.setValue(value)

    @property
    def text_output(self):
        return self.ui.detected.text()

    @text_output.setter
    def text_output(self, text):
        self.ui.detected.setText(text)
    
    @property
    def audio_sample_size(self):
        """ Audio window size in byte: sample_rate * window_size * encoding"""
        return int(self.sample_rate * self.project.features_info['sample_t'] * 2)
    
class Activation_Sample(QtWidgets.QWidget):
    deleted = QtCore.pyqtSignal(QtWidgets.QListWidgetItem, name='deleted')
    def __init__(self, data: "Audio data", label: "Activated class", choices: "hotword list", player: "Sound player", list_item: "QListWidgetItem"):
        super().__init__()
        self.list_item = list_item
        self.player = player
        self.data = data
        self.label = label
        self.CB = QtWidgets.QCheckBox("{}".format(self.label))
        self.play_PB = QtWidgets.QPushButton()
        play_icon = QtGui.QPixmap(os.path.join(DIR_PATH, "icons/play.png"))
        self.play_PB.setIcon(QtGui.QIcon(play_icon))
        self.play_PB.setIconSize(QtCore.QSize(20,20))
        self.delete_PB = QtWidgets.QPushButton()
        cancel_icon = QtGui.QPixmap(os.path.join(DIR_PATH, "icons/cancel.png"))
        self.delete_PB.setIcon(QtGui.QIcon(cancel_icon))
        self.delete_PB.setIconSize(QtCore.QSize(20,20))
        self.hotword_CB = QtWidgets.QComboBox()
        for c in choices:
            self.hotword_CB.addItem(c)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.CB)
        layout.addWidget(self.play_PB)
        layout.addWidget(self.hotword_CB)
        layout.addWidget(self.delete_PB)
        layout.addStretch()
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)
        
        self.play_PB.clicked.connect(self.play_sample)
        self.delete_PB.clicked.connect(self.delete)

    def play_sample(self):
        self.player.play_from_buffer(self.data)

    def delete(self):
        self.deleted.emit(self.list_item)

