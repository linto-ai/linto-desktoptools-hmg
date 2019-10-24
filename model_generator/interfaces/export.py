import os
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from interfaces.scrollMessageBox import ScrollMessageBox

import tensorflow as tf
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
        tf.saved_model.save(model, export_folder)
        QtWidgets.QMessageBox.information(self, "Model exported", "Saved model exported at {}".format(export_folder))

    def export_TensorflowLite(self):
        # https://www.tensorflow.org/lite/guide/ops_select
        converter = tf.lite.TFLiteConverter.from_keras_model_file(self.project.model_path)
        converter.allow_custom_ops = True
        converter.target_ops = []
        if self.ui.TFLITE_BI_CB.isChecked() : converter.target_ops.append(tf.lite.OpsSet.TFLITE_BUILTINS)
        if self.ui.TFLITE_BI_CB.isChecked() : converter.target_ops.append(tf.lite.OpsSet.SELECT_TF_OPS)
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
        man['input_shape'] = self.project.model_info['input_shape']
        man['n_hotword'] = len(self.project.project_info['hotwords'])
        man['wakeword_index'] = 0
        man['inference_step'] = 1
        man['features'] = dict()
        man['features']['features'] = self.project.features_info['features_param']
        man['features']['sample_rate'] = self.project.features_info['sample_rate']
        man['features']['window_d'] = self.project.features_info['window_t']
        man['features']['stride_d'] = self.project.features_info['hop_t']
        man['features']['emphasis'] = self.project.features_info['emphasis']

        with open(file_path, 'w') as f:
            json.dump(man, f)