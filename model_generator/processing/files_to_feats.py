import wavio
from base import _Feature
import numpy as np

def file_to_feat(filePath: str, feat_param : _Feature, autoTrim: True, zeroPadding: True):
    content = wavio.read(filePath)
    if content.rate != feat_param.sample_rate:
        raise Exception("{} : Error Wrong sampling rate ({})".format(filePath, content.rate))
    data = content.data
    if data.shape[-1] != 1: # Keep first channel only 
        data = data[:,1]
    data = np.squeeze(data)
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

def files_to_feat(file_list: list, feat_param : _Feature, autoTrim: True, zeroPadding: True):
    features = []
    for f in file_list:
        try:
            feats = file_to_feat(f, feat_param, autoTrim, zeroPadding)
        except Exception as e:
            print(e)
        else:
            features.append(feats)
    return np.array(features)