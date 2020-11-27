import json

class _Feature:
    sample_rate = 16000
    encoding = 2
    sample_length = 1.0
    use_emphasis = True
    emphasis_factor = 0.97
    window_length = 0.064
    window_stride = 0.032
    window_fun = None

    feature_type = None

    def __init__(self, name, values : dict = None):
        self.name = name
        if values is not None:
            self.loadValues(values)

    def loadValues(self, values : dict):
        for key in values.keys():
            if key in _Feature.__dict__.keys():
                self.__setattr__(key, values[key])
    
    def write(self, filePath):
        pass

    def generateManifest(self):
        output = dict()
        output["name"] = self.name
        output["acoustic"] = dict()
        for attr in ["sample_rate", "encoding", "sample_length", "use_emphasis", "emphasis_factor", "window_length", "window_stride", "window_fun"]:
            output["acoustic"][attr] = self.__getattribute__(attr)
        output["feature_type"] = self.feature_type
        return output



class MFCC_Features(_Feature):
    fft_size = 512
    n_filters = 20
    n_coefs = 13
    use_logenergy = False

    def __init__(self, name, values : dict = None):
        _Feature.__init__(self, name, values)
        self.feature_type = "mfcc"

    def generateManifest(self):
        output = super().generateManifest()
        output["feature_params"] = dict()
        for attr in ["fft_size", "n_filters", "n_coefs", "use_logenergy"]:
            output["feature_params"][attr] = self.__getattribute__(attr)

        return output