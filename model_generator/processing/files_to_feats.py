import os
import numpy as np
from librosa import load as loadAudio
from base import _Feature
from base import DataSet

def file_to_feat(filePath: str, feat_param : _Feature, autoTrim: bool = True, zeroPadding: bool = True):
    data = loadAudio(filePath, sr=feat_param.sample_rate)[0]

    if len(data) > feat_param.sample_s and autoTrim: # Trim longer sample (centered)
        excess = len(data) - feat_param.sample_s
        data = data[excess // 2 : -(excess //2)]
    elif len(data) < feat_param.sample_s: # Zero-pad short sample (centered)
        if zeroPadding:
            lack = feat_param.sample_s - len(data)
            data = np.concatenate([np.zeros(lack // 2), data, np.zeros(lack // 2 + 1)])
        else:
            raise Exception("{} : Sample too short ({}/{})".format(filePath, len(data), feat_param.sample_s))

    return feat_param.extract_function(data)

def files_to_feat(file_list: list, feat_param : _Feature, autoTrim: bool = True, zeroPadding: bool = True):
    features = []
    for f in file_list:
        try:
            feats = file_to_feat(f, feat_param, autoTrim, zeroPadding)
        except Exception as e:
            print(e)
        else:
            features.append(feats)
    return np.array(features)

def createOutputs(labels: list) -> dict:
    """ Create output arrays by label """
    outputFormat = dict()
    outputFormat[""] = np.zeros(len(labels))
    for i, label in enumerate(labels):
        arr = np.zeros(len(labels))
        arr[i] = 1.0
        outputFormat[label] = arr
    return outputFormat

def prepare_input_output(dataset: DataSet, features: _Feature, save_features_folder: str = None, traceCallBack = None) -> tuple:
    """ Generate input / output from a dataset """
    labels = createOutputs(dataset.labels)
    save_feature = save_features_folder is not None
    inputs = []
    outputs = []
    n_sample = len(dataset.samples)
    for i, sample in enumerate(dataset.samples):
        try:
            if sample.featureFile is not None:
                try:
                    feats = loadFeatureFile(sample.featureFile, features.feature_shape)
                except Exception as e:
                    feats = file_to_feat(sample.file, features)
                    sample.featureFile = None
            else:
                feats = file_to_feat(sample.file, features)
                if save_feature:
                    featFile = os.path.join(save_features_folder, os.path.basename(sample.file) + ".feat")
                    sample.featureFile = featFile
                    writeFeatureFile(featFile, feats)
                
        except Exception as e:
            print("Failed to extract parameter from {}: {}".format(sample.file, e))
            continue
        else:
            inputs.append(feats)
            outputs.append(labels[sample.label])
        if traceCallBack is not None:
            traceCallBack("Extracting features from {}: {}/{}".format(dataset.dataSetName, i, n_sample))
    inputs = np.array(inputs)
    outputs = np.array(outputs)

    if save_features_folder is not None:
        dataset.saveDataSet()
    return inputs, outputs

def writeFeatureFile(filePath: str, content: np.ndarray):
    with open(filePath, 'bw') as f:
        content.tofile(f)

def loadFeatureFile(filePath :str, shape: tuple) -> np.array:
    with open(filePath, 'br') as f:
        feats = np.fromfile(f)
    return feats.reshape(shape)


