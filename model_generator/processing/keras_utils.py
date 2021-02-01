from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, Callback
from tensorflow.keras.models import load_model

class Epoch_CallBack(Callback):
    def __init__(self, callback_fun):
        super().__init__()
        self.callback_fun = callback_fun

    def on_epoch_end(self, epoch, logs={}):
        self.callback_fun(epoch, logs)


def callbacksDef(model_path, updateFun, keep_best_only: bool = False):
    checkpoint = ModelCheckpoint(model_path, save_best_only=keep_best_only)
    return [checkpoint, Epoch_CallBack(updateFun)]

def loadModel(modelPath: str):
    return load_model(modelPath)