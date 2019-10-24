import os
from threading import Thread
from multiprocessing import cpu_count, Pool

import numpy as np
import wavio
from sonopy import mfcc_spec

from .signal_processing import pre_emphasis

supported_features = ['mfcc', 'lmfe']

def wav2features(wav_file: str,
                 parameters: dict,
                 normalize: bool = True,
                 allow_zero_padding: bool = False):
    '''
    Extract audio features from a wave file.

    Keyword Parameters:
    ===================
    - wave_file (str) -- wave file path
    - parameters (dict) -- audio and feature parameters used to extract features
    - normalize (bool) -- normalize audio before processing (default True)
    - allow_zero_padding (bool) -- add zeros if input audio features are too short (default False)

    Returns
    =======
    features (np.array) -- return an np.array of size parameters['shape']

    ### Raises
    - ValueError -- Wrong parameters

    '''
    output_shape = parameters['shape']
    features_param = parameters['features_param']

    if features_param['feature_type'] not in supported_features:
        raise ValueError("Unsupported feature type {}, supported features are: {}".format(features_param['feature_type'], 
                                                                                          supported_features))
    try:
        with open(wav_file, 'rb') as fp:
            wav = wavio.read(fp)
    except:
        raise FileNotFoundError("File not found")
    if wav.data.dtype != np.int16:
        raise ValueError('Unsupported data type: ' + str(wav.data.dtype))
    if wav.rate != parameters['sample_rate']:
        raise ValueError('Unsupported sample rate: ' + str(wav.rate))

    signal = np.squeeze(wav.data)

    if 'emphasis' in parameters and parameters['emphasis'] is not None:
        signal = pre_emphasis(signal, parameters['emphasis'])

    if normalize:
        signal = signal.astype(np.float32) / abs(float(np.iinfo(np.int16).min))
    
    features = signal2features(signal, parameters, features_param)
    
    # Check output length
    if len(features) < output_shape[0]:
        if allow_zero_padding:
            features = np.vstack((np.zeros((output_shape[0] - len(features), len(features[0]))),features))
        else:
            return None
    if len(features) > output_shape[0]:
        features = features[:output_shape[0]]

    return features

def signal2features(signal, audio_parameters, features_param):
    if features_param['feature_type'] == 'mfcc':
        remove_energy = not features_param.get('energy', False)
        features = mfcc_spec(signal,
                            audio_parameters['sample_rate'],
                            (int(audio_parameters['window_t'] * audio_parameters['sample_rate']), int(audio_parameters['hop_t'] * audio_parameters['sample_rate'])),
                            num_filt=features_param['n_filt'],
                            fft_size=features_param['n_fft'],
                            num_coeffs=features_param['n_coef'] + remove_energy)
        if remove_energy:
            features = features[:, 1:]
    
    elif features_param['feature_type'] == 'lmfe':
        features = mfcc_spec(signal,
                            audio_parameters['sample_rate'],
                            (int(audio_parameters['window_t'] * audio_parameters['sample_rate']), int(audio_parameters['hop_t'] * audio_parameters['sample_rate'])),
                            num_filt=features_param['n_filt'],
                            fft_size=features_param['n_fft'],
                            num_coeffs=features_param['n_coef'],
                            return_parts=True)[2][:,:features_param['n_coef']]
    # Insert new features here

    return features

def folder2features(folder: str, 
                    parameters: dict,
                    normalize: bool = True,
                    allow_zero_padding: bool = False):
    """ Extracts features for every wave file in the specified folder
    
    Keyword Parameters:
    ===================
    - folder (str) -- folder containing the files to process
    - parameters (dict) -- audio and feature parameters used to extract features
    - normalize (bool) -- normalize audio before processing (default True)
    - allow_zero_padding (bool) -- add zeros if input audio features are too short (default False)
    """
    list_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.wav')]
    return files2features(list_files, parameters, normalize, allow_zero_padding)

def files2features(file_list,
                   parameters,
                   normalize: bool = True,
                   allow_zero_padding: bool = False,
                   labels = None,
                   return_file = False,
                   progress_callback = None):
    """
    Extracts features from a list of files

    Keyword Parameters:
    ===================
    - file_list (iterable) -- list of file paths
    - parameters (dict) -- audio and feature parameters used to extract features
    - normalize (bool) -- normalize audio before processing (default True)
    - allow_zero_padding (bool) -- add zeros if input audio features are too short (default False)
    - labels (Any) -- Ignored if is None, else append label to the return value (default None)
    - return_file (bool) -- if true, first return value is the file_path list
    - progress_callback (callable) -- called at each iteration with parameter tuple (current_index, total, text)
    """
    
    single_label = not hasattr(labels, '__iter__')
    use_labels = labels is not None
    if use_labels:
        if not single_label:
            assert len(labels) == len(file_list), "Label list length and file list length are different"
            output_labels = np.zeros((len(file_list), len(labels[0])))
        else:
            output_labels = np.full((len(file_list), len(labels)), labels)
    
    features = np.zeros((len(file_list), *parameters['shape']))
    files = []
    
    n = 0
    for i, f in enumerate(file_list):
        if progress_callback is not None:
            progress_callback(i, len(file_list), "Extracting features")
        try:
            feats = wav2features(f, parameters, normalize, allow_zero_padding)
        except Exception as e:
            print("Could not process file {} : {}".format(f, e.args))
            continue
        if feats is not None:
            features[n] = feats
        else:
            continue
        files.append(f)
        if use_labels:
            if not single_label:
                output_labels[n] = labels[i]
        n+=1
    
    if any([use_labels, return_file]):
        return_array = []
        if return_file: return_array.append(files)
        return_array.append(features[:n])
        if use_labels: return_array.append(output_labels[:n])
        return return_array
    else:
        return features[:n]

