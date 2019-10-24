import os
from random import shuffle

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from uuid import uuid4

from interfaces.ui.addtoset_ui import Ui_AddToSet
from scripts.keras_functions import load_model
from scripts.audio_io import save_audio

class AddToSet(QtWidgets.QDialog):
    samples_added = QtCore.pyqtSignal(name='samples_added')
    def __init__(self, parent, manifest, manifest_path, samples):
        super().__init__(parent)
        self.ui = Ui_AddToSet()
        self.ui.setupUi(self)
        self.manifest = manifest
        self.manifest_path = manifest_path
        self.samples = samples
        self.n_samples = len(samples)
        self.added_to_folder = False
        self.added_to_sets = False

        #connects
        self.ui.close_PB.clicked.connect(self.close)
        self.ui.add_samples_PB.clicked.connect(self.save_samples)
        self.ui.add_to_project.toggled.connect(self.ui.addto_GB.setEnabled)
        self.ui.browse_PB.clicked.connect(self.browse_folder)

    def save_to_sets(self, folder):
        if self.added_to_sets:
            return
        target_set = 'train'
        if self.ui.val_CB.isChecked():
            target_set = 'validation'
        elif self.ui.test_CB.isChecked():
            target_set = 'test'
        
        for sample in self.samples:
            file_name = self.ui.name_format.text().replace('%(label)', sample[0]).replace('%(uuid)', str(uuid4())) + '.wav'
            file_path = os.path.join(folder, target_set, sample[0], file_name)
            print(file_path)
            save_audio(np.frombuffer(sample[1], dtype=np.int16), file_path, 16000)
        self.added_to_sets = True

    def save_to_folder(self, folder):
        # Check folders
        if self.added_to_folder:
            return
        if not os.path.isdir(folder):
            os.mkdir(folder)
        for label in ['non-hotword'] + self.manifest['general']['hotwords']:
            target_dir = os.path.join(folder, label)
            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)
        
        for sample in self.samples:
            file_name = self.ui.name_format.text().replace('%(label)', sample[0]).replace('%(uuid)', str(uuid4())) + '.wav'
            file_path = os.path.join(folder, sample[0], file_name)
            print(file_path)
            save_audio(np.frombuffer(sample[1], dtype=np.int16), file_path, 16000)
        self.added_to_folder = True
        
    def save_samples(self):
        if self.ui.add_to_project.isChecked():
            folder = os.path.dirname(self.manifest['model']['model_path'])
            self.save_to_sets(folder)
        else:
            if os.path.isdir(self.ui.save_target.text()):
                folder = self.ui.save_target.text()
            else:
                folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", "/home/")
                if folder is None:
                    return
            self.save_to_folder(folder)
        self.samples_added.emit()

    def browse_folder(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", "/home/")
        if res is not None:
            self.ui.save_target.setText(res)