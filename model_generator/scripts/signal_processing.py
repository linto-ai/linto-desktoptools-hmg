import numpy as np

def pre_emphasis(sig: np.array, factor: float, previous_value=None):
    """ Apply pre-emphasis to the signal

        Keyword arguments:
        ==================  
        - sig (np.array) -- the input signal
        - factor (float) -- the emphasis factor
        - previous_value (num) -- for real time processing. Is the last value of the previous frame
    """
    if previous_value is not None:
        return (sig - factor * np.append(previous_value, sig[:-1]))
    return np.append(sig[0], sig[1:] - factor * sig[:-1])

    