import json

from processing.mfcc import mfcc_feats

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

    def __init__(self, name : str, featureFile: str, values : dict = None,):
        self.name = name
        self.featureFile = featureFile
        if values is not None:
            self.loadValues(values)

    def loadValues(self, values : dict):
        for key in values.keys():
            if key in _Feature.__dict__.keys():
                self.__setattr__(key, values[key])
    
    def write(self, filePath):
        pass

    def getParameters(self) -> dict:
        return dict()

    def generateManifest(self):
        output = dict()
        output["name"] = self.name
        output["acoustic"] = dict()
        for attr in ["sample_rate", "encoding", "sample_length", "use_emphasis", "emphasis_factor", "window_length", "window_stride", "window_fun"]:
            output["acoustic"][attr] = self.__getattribute__(attr)
        output["feature_type"] = self.feature_type
        return output

    def extract_function(self) -> callable:
        return lambda x : None

    @property
    def sample_s(self):
        return int(self.sample_length * self.sample_rate)

    @property
    def window_s(self):
        return int(self.window_length * self.sample_rate)
    
    @property
    def window_stride_s(self):
        return int(self.window_stride * self.sample_rate)


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

    def loadValues(self, values: dict):
        acoustic = values["acoustic"] if "acoustic" in values.keys() else values
        super().loadValues(acoustic)
        feat_params = values["feature_params"] if "feature_params" in values.keys() else values
        for key in feat_params:
            if key in MFCC_Features.__dict__.keys():
                self.__setattr__(key, feat_params[key])

    def getParameters(self):
        return {"fft_size" : self.fft_size,
                "n_filters" : self.n_filters,
                "n_coefs" : self.n_coefs,
                "use_logenergy" : self.use_logenergy}

    def write(self):
        with open(self.featureFile, 'w') as f:
            json.dump(self.generateManifest(), f)

    def extract_function(self, sig) :
        return mfcc_feats(sig,
                    self.sample_rate, 
                    self.window_s, 
                    self.window_stride_s, 
                    self.fft_size, 
                    num_filter = self.n_filters, 
                    num_coef = self.n_coefs, 
                    hamming = self.window_fun == 'hamming',
                    preEmp  = self.emphasis_factor)

def getFeaturesByType(featType: str, name : str):
    if featType.lower() == "mfcc":
        return MFCC_Features(name)
    else:
        return None