# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import *

from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, Callback

LOSS_BIAS = 0.9

def set_loss_bias(bias: float):
    """
    Near 1.0 reduces false positives
    Near 0.0 reduces false negatives
    """
    global LOSS_BIAS
    LOSS_BIAS = bias


def weighted_log_loss(yt, yp) -> Any:
    """
    Binary crossentropy with a bias towards false negatives
    yt: Target
    yp: Prediction
    """
    from tensorflow.keras import backend as K

    pos_loss = -(0 + yt) * K.log(0 + yp + K.epsilon())
    neg_loss = -(1 - yt) * K.log(1 - yp + K.epsilon())

    return LOSS_BIAS * K.mean(neg_loss) + (1. - LOSS_BIAS) * K.mean(pos_loss)


def weighted_mse_loss(yt, yp) -> Any:
    from tensorflow.keras import backend as K

    total = K.sum(K.ones_like(yt))
    neg_loss = total * K.sum(K.square(yp * (1 - yt))) / K.sum(1 - yt)
    pos_loss = total * K.sum(K.square(1. - (yp * yt))) / K.sum(yt)

    return LOSS_BIAS * neg_loss + (1. - LOSS_BIAS) * pos_loss

def load_keras() -> Any:
    from tensorflow import keras
    keras.losses.weighted_log_loss = weighted_log_loss
    return keras

def create_model(model_path, 
                 input_shape: tuple,
                 n_denses: int = 0, 
                 dense_sizes:list = None, 
                 dropout: int = 0, 
                 output_size: int = 1, 
                 loss_fun: int =1, 
                 loss_bias=0.9, 
                 metrics=['accuracy'], 
                 noise_layer_derivation = None,
                 unroll: bool = False):
    from tensorflow import keras

    model = keras.models.Sequential()

    model.add(keras.layers.GRU(input_shape[0],
                           activation='linear',
                           input_shape=input_shape,
                           name='GRU_layer',
                           unroll=unroll))
    
    if noise_layer_derivation is not None:
        model.add(keras.layers.GaussianNoise(noise_layer_derivation))

    if dropout > 0:
        model.add(keras.layers.Dropout(dropout))
        
    if n_denses > 0:
        for i, size in enumerate(dense_sizes):
            model.add(keras.layers.Dense(size, activation='relu', name="dense_{}".format(i + 1)))
    model.add(keras.layers.Dense(output_size, activation='sigmoid', name='output'))

    load_keras()
    loss = weighted_log_loss if loss_fun == 1 else 'mean_squared_error' 
    set_loss_bias(loss_bias)
    model.compile('rmsprop', loss, metrics=metrics)
    return model

def callbacks(model_path, keep_best_only: bool = False):
    checkpoint = ModelCheckpoint(model_path, save_best_only=keep_best_only)
    model_base = model_path.split('.')[0]
    return [checkpoint, TensorBoard(log_dir=model_base + '.logs')]
 
def load_model(model_path):
    return load_keras().models.load_model(model_path)

class Epoch_CallBack(Callback):
    def __init__(self, callback_fun):
        super().__init__()
        self.callback_fun = callback_fun

    def on_epoch_end(self, epoch, logs={}):
        self.callback_fun(epoch, logs)