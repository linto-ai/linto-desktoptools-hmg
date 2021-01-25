import time

from PyQt5 import QtCore

import numpy as np
import pyaudio

from base import _Feature
from processing.keras_utils import loadModel
from processing.mfcc import mfcc_feats

class InferenceEngine(QtCore.QObject):

    prediction = QtCore.pyqtSignal(float, list, name='project_updated') # On prediction emit (x_value, [predictions])
    sample_detected = QtCore.pyqtSignal(bytes, int, name='sample_detected') # On prediction emit (x_value, [predictions])

    
    def __init__(self, features: _Feature, modelPath: str, threshold: float):
        QtCore.QObject.__init__(self)
        self.features = features
        self.threshold = threshold

        self.isRunning = False
        self.audio = None

        self.signalBuffer = None
        self.featuresBuffer = None
        self.currentSignal = b"" # Audio signal corresponding to features being infered
        self.triggeringSignal = b""
        self.timeStamp = 0.0

        self.f_det = False
        self.f_cp = -1

        self.model = loadModel(modelPath)

        self.extractFun = self.features.extract_function

    def init_audio(self):
        self.featuresBuffer = np.zeros(self.features.feature_shape)
        self.signalBuffer = np.array([])
        if self.audio is None:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.features.sample_rate,
                            input=True,
                            frames_per_buffer=self.features.window_stride_s,
                            stream_callback=self._onFrame,
                            start=False)

    def startInference(self):
        if not self.isRunning:
            if self.audio == None:
                self.init_audio()
            self.currentSignal = bytes([0] * self.features.sample_s * 2)
            self.timeStamp = 0.0
            self.isRunning = True
            self.stream.start_stream()

    def stopInference(self):
        if self.isRunning:
            self.stream.stop_stream()
            self.isRunning = False
            self.featuresBuffer = np.zeros(self.features.feature_shape)

    def _onFrame(self, in_data, frame_count, time_info, status):
        """ Called on every new audio frame"""
        self.currentSignal += in_data
        self.timeStamp += self.features.window_stride
        frame = np.frombuffer(in_data, dtype='<i2').astype(np.float32, order='C') / 32767.0
        self.signalBuffer = np.concatenate([self.signalBuffer, frame])
        if len(self.signalBuffer) >= self.features.window_s:
            feats = self.extractFun(self.signalBuffer)
            self.signalBuffer = self.signalBuffer[self.features.window_stride_s * len(feats):]
            self.currentSignal = self.currentSignal[len(in_data):]
            self.featuresBuffer = np.concatenate([self.featuresBuffer, feats])[len(feats):]
            pred = self.model.predict(self.featuresBuffer[np.newaxis])
            self.prediction.emit(self.timeStamp, list(pred))
            self._onPrediction(pred)
        return (None, pyaudio.paContinue)

    def _onPrediction(self, predictions):
        """ Called everytime a prediction is made"""
        if any(predictions > self.threshold):
            cp = np.argmax(predictions)
            if not self.f_det:
                self.f_det = True
                self.triggeringSignal = self.currentSignal
                self.f_cp = cp
            else:
                if self.f_cp == cp:
                    self.triggeringSignal += self.currentSignal[-self.features.window_stride_s *2:] # Last frame size *2 (2B)
                else:
                    self.sample_detection.emit(self.triggeringSignal, self.f_cp)
                    self.f_cp = cp
                    self.triggeringSignal = self.currentSignal
        elif self.f_det:
            self.sample_detected.emit(self.triggeringSignal, self.f_cp)
            self.f_det = False
                

