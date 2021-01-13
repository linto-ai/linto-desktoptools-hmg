import numpy as np

from scripts.keras_functions import load_model

class PredictFun(object):
    def __init__(self, model_path: str):
        assert model_path.endswith('.hdf5'), "Supported model files are .hdf5"      
        self._predict_fun = self._load_keras_model(model_path)

    def _load_keras_model(self, model_path : str):
        self.model = load_model(model_path)
        #self.model._make_predict_function()
        return self.model.predict
    
    def predict(self, inputs):
        return self._predict_fun(inputs)