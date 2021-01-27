import os

import tensorflowjs as tfjs

from base.model import _Model, _Layer, GRU_Layer
from .keras_utils import loadModel
from tensorflow.keras.models import save_model
from tensorflow import lite as tflite
def isTFLiteCompatible(model: _Model) -> tuple:
    for layer in model.layers:
        if type(layer) is GRU_Layer:
            if layer.unroll == False:
                return (False, "TFLite doesn't support unrolled GRU.")
    return (True, "")

def isTFJSCompatible(model: _Model) -> tuple:
    for layer in model.layers:
        if type(layer) is GRU_Layer:
            if layer.reset_after == False:
                return (False, "TFJS models need the GRU flag reset_after set to True.")
    return (True, "")

def exportTFLite(modelPath: str, targetPath: str):
    model = loadModel(modelPath)
    try:
        converter = tflite.TFLiteConverter.from_keras_model(model)
        tf_lite_model = converter.convert()
        with open(targetPath, 'wb') as f:
            f.write(tf_lite_model)
    except Exception as e:
        raise Exception("Failed to export to TFLile format : {}".format(e))

def exportKeras(modelPath: str, targetPath: str):
    model = loadModel(modelPath)
    save_model(model, targetPath)

def exportTFJS(modelPath, targetFolder):
    if not os.path.isdir(targetFolder):
        try:
            os.mkdir(targetFolder)
        except:
            raise Exception("Could not create folder {}".format(targetFolder))

    model = loadModel(modelPath)
    
    try:
        tfjs.converters.save_keras_model(model, targetFolder)
    except Exception as e:
        raise Exception("Failed to export to TFJS format: {}".format(e))
