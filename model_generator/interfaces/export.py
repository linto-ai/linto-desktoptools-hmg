import os
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from interfaces.scrollMessageBox import ScrollMessageBox

from tensorflow import saved_model, lite
from interfaces.ui.export_ui import Ui_Export
from scripts.keras_functions import load_model

class Export(QtWidgets.QWidget):

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Export()
        self.ui.setupUi(self)
        self.project = project

        #Connects
        self.ui.tensorflowJS_PB.clicked.connect(self.export_TensorflowJS)
        self.ui.tensorflow_PB.clicked.connect(self.export_TF_PB)
        self.ui.manifest_PB.clicked.connect(self.export_manifest)
        self.ui.TFLite_PB.clicked.connect(self.export_TensorflowLite)

    
    def export_TensorflowJS(self):
        import tensorflowjs as tfjs
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a target directory", "/home/")
        if dir_path:
            model = load_model(self.project.model_path)
            tfjs.converters.save_keras_model(model, dir_path)

    def export_TF_PB(self):
        model = load_model(self.project.model_path)
        export_folder = os.path.join(self.project.project_location, "output/{}/{}/".format(self.project.project_info['project_name'], self.ui.version_SB.value()))
        saved_model.save(model, export_folder)
        QtWidgets.QMessageBox.information(self, "Model exported", "Saved model exported at {}".format(export_folder))

    def export_TensorflowLite(self):
        model = load_model(self.project.model_path)
        converter = lite.TFLiteConverter.from_keras_model(model)
        
        try:
            tflite_model = converter.convert()
        except Exception as e:
            error_box = QtWidgets.QMessageBox(self)
            error_box.setIcon(QtWidgets.QMessageBox.Warning)
            error_box.setText("Unable to create the tensorflowLite model, see logs")
            error_box.setWindowTitle("Error")
            error_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            res = error_box.exec()
            print(str(e))
        else:
            gen_name = self.project.project_info.get('project_name', 'model') + ".tflite"
            file_path = QtWidgets.QFileDialog.getSaveFileName(self, "Save model parameter file", os.path.join(self.project.project_location, gen_name), "TFLite File (*.tflite)")[0]
            if file_path is None or len(file_path) == 0:
                return
            with open(file_path, "wb") as f:
                f.write(tflite_model)

    def export_manifest(self):
        gen_name = self.project.project_info.get('project_name', 'model') + ".param"
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, "Save model parameter file", os.path.join(self.project.project_location, gen_name), "Parameter File (*.param)")[0]
        if file_path is None or len(file_path) == 0:
            return
        man = dict()

        man['model_name'] = self.project.project_info['model_name']
        man['input_shape'] = self.project.model_info['input_shape']
        man['n_hotword'] = len(self.project.project_info['hotwords'])
        
        man['audio'] = dict()
        man['audio']['sample_rate'] = self.project.features_info['sample_rate']
        man['audio']['window_d'] = self.project.features_info['window_t']
        man['audio']['stride_d'] = self.project.features_info['hop_t']
        man['audio']['emphasis'] = self.project.features_info['emphasis']

        man['features'] = self.project.features_info['features_param']
        
        

        with open(file_path, 'w') as f:
            json.dump(man, f)