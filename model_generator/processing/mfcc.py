import numpy as np
from functools import lru_cache
from scipy.fftpack import dct

def safe_log(x):
    """Prevents error on log(0) or log(-1)"""
    return np.log(np.clip(x, np.finfo(float).eps, None))

def split(array, window_size, window_stride):
    n_win = int(np.floor((len(array) - window_size) / window_stride) + 1)
    return np.array([array[i*window_stride: i*window_stride+window_size] for i in range(n_win)])

@lru_cache
def hamming_fun(length):
    return np.hamming(length)

def do_hamming(frame: np.array):
    ''' applies hamming window function'''
    return frame * hamming_fun(frame.shape[-1])

def preEmphasis(signal, factor=0.97):
    return signal - np.concatenate([[0], signal[:-1] * factor])

def power_spec(frames, fft_size=512):
    """Calculates power spectrogram"""
    fft = np.fft.rfft(frames, n=fft_size)
    return fft.real ** 2 + fft.imag ** 2

@lru_cache()  # Prevents recalculating when calling with same parameters
def mel_filter(sample_rate, num_filt, input_length):
    
    def hertz_to_mels(f):
        return 1127. * np.log(1. + f / 700.)

    def mel_to_hertz(mel):
        return 700. * (np.exp(mel / 1127.) - 1.)    

    mels_v = np.linspace(hertz_to_mels(0), hertz_to_mels(sample_rate), num_filt + 2, True)
    hertz_v = mel_to_hertz(mels_v)
    indexes = (hertz_v * input_length / sample_rate).astype(int)

    filters = np.zeros([num_filt, input_length])

    for i, (left, middle, right) in enumerate(split(indexes, 3,1)):
        filters[i, left:middle] = np.linspace(0., 1., middle - left, False)
        filters[i, middle:right] = np.linspace(1., 0., right - middle, False)

    return filters

def lmfe_feats(signal, 
         sample_rate, 
         window_length, 
         window_stride, 
         fft_size, 
         num_filter: int = 20,
         hamming: bool = False,
         preEmp : float = 0.97,):
    frames = split(preEmphasis(signal, preEmp), window_length, window_stride)
    if hamming:
        frames = do_hamming(frames)
    pow_spec = power_spec(frames, fft_size)
    return safe_log(np.dot(pow_spec, mel_filter(sample_rate // 2, num_filter, pow_spec.shape[-1]).T))


def mfcc_feats(signal, 
         sample_rate, 
         window_length, 
         window_stride, 
         fft_size, 
         num_filter: int = 20, 
         num_coef: int = 13, 
         hamming: bool = False,
         preEmp : float = 0.97,):
    
    lmfe = lmfe_feats(signal, sample_rate, window_length, window_stride, fft_size, num_filter, hamming, preEmp)
    mfccs = dct(lmfe, norm='ortho')
    return mfccs[::,1:num_coef+1]