import json

class _Layer:
    name = None
    def __init__(self, is_input: bool = False, is_output: bool = False, is_required: bool = False):
        self.is_input = is_input
        self.is_output = is_output
        self.is_required = is_required

    def toDict(self) -> dict:
        layer_dict = dict()
        layer_dict["type"] = self.name
        layer_dict["is_input"] = self.is_input
        layer_dict["is_output"] = self.is_output
        layer_dict["is_required"] = self.is_required
        return layer_dict

    def loadValue(self, values: dict):
        for key in values.keys():
            if key in _Layer.__dict__.keys():
                self.__setattr__(key, values[key])
    
    def getEditableParameters(self) -> dict:
        ''' Return configurables parameters and types for ListItem creation'''
        return list()
        
class GRU_Layer(_Layer):
    name = "gru"
    gru_act = ["linear", "tanh"]
    def __init__(self,
                 n_cell: int = 30,
                 activation_fun: str = "linear",
                 is_input: bool = True, 
                 is_output: bool = False,
                 unroll: bool = False,
                 reset_after: bool = False,
                 is_required: bool = False):
        _Layer.__init__(self, is_input, is_output, is_required)
        
        self.n_cell = n_cell
        self.activation_fun = activation_fun
        self.unroll = unroll
        self.reset_after = reset_after
    
    def toDict(self) -> dict:
        layer_dict = _Layer.toDict(self)
        layer_dict["n_cell"] = self.n_cell
        layer_dict["activation_fun"] = self.activation_fun
        layer_dict["unroll"] = self.unroll
        layer_dict["reset_after"] = self.reset_after
        return layer_dict

    def loadValue(self, values: dict):
        _Layer.loadValue(self, values)
        for key in values.keys():
            if key in GRU_Layer.__dict__.keys():
                self.__setattr__(key, values[key])
                
    def getEditableParameters(self) -> dict:
        ''' Return configurables parameters and types for ListItem creation'''
        params = []
        params.append(("n_cell", int, self.n_cell))
        params.append(("activation_fun", list, self.activation_fun, GRU_Layer.gru_act))
        params.append(("unroll", bool, self.unroll))
        params.append(("reset_after", bool, self.reset_after))
        return params

class Dense_Layer(_Layer):
    name = "dense"
    dense_act = ["relu", "sigmoid", "linear"]
    def __init__(self,
                 n_cell: int = 30,
                 activation_fun: str = "relu",
                 is_input: bool = True, 
                 is_output: bool = False,
                 is_required: bool = False):
        _Layer.__init__(self, is_input, is_output, is_required)
        self.n_cell = n_cell
        self.activation_fun = activation_fun
        
    def toDict(self) -> dict:
        layer_dict = _Layer.toDict(self)
        layer_dict["n_cell"] = self.n_cell
        layer_dict["activation_fun"] = self.activation_fun
        return layer_dict
    
    def getEditableParameters(self) -> dict:
        ''' Return configurables parameters and types for ListItem creation'''
        params = []
        params.append(("n_cell", int, self.n_cell))
        params.append(("activation_fun", list, self.activation_fun, Dense_Layer.dense_act))
        return params

class Output_Layer(_Layer):
    name = "output"
    def __init__(self, 
                 n_cell,
                 activation_fun: str = "sigmoid",
                 is_input: bool = True, 
                 is_output: bool = False,
                 is_required: bool = True):
        _Layer.__init__(self, is_input, is_output, is_required)
        self.n_cell = n_cell
        
    def toDict(self) -> dict:
        layer_dict = _Layer.toDict(self)
        layer_dict["n_cell"] = self.n_cell
        layer_dict["activation_fun"] = "sigmoid"
        return layer_dict

class _Model:
    allowed_layers = []
    def __init__(self, name: str):
        self.modelPath = ''
        self.name = name
        self.type = "void"
        self.layers = []
        
    def toDict(self) -> dict:
        manifest = dict()
        manifest["name"] = self.name
        manifest["type"] = self.type
        manifest["layers"] = [l.toDict() for l in self.layers]
        return manifest
    
    def loadModel(self, modelPath: str):
        pass

    def writeModel(self, modelPath: str = None):
        if modelPath is None:
            modelPath = self.modelPath
        manifest = self.toDict()
        try:
            with open(modelPath, 'w') as f:
                json.dump(manifest, f)
        except Exception as e:
            raise Exception("Could not write model at {}: {}".format(modelPath, e))

class GRU_Model(_Model):
    allowed_layers = ["gru", "dense"]
    def __init__(self, name: str = "", layers: list = None):
        _Model.__init__(self, name)
        self.type = "gru"
        self.layers = [
            GRU_Layer(is_input=True, is_required=True),
            Dense_Layer(),
            Output_Layer(1)
        ]

    def loadModel(self, modelPath: str):
        self.layers = []
        try:
            with open(modelPath, "r") as f:
                manifest = json.load(f)
        except:
            raise Exception("Could not read model manifest at {}".format(modelPath))
        try:
            self.name = manifest["name"]
            for layer in manifest["layers"]:
                layer_type = layer.pop("type")
                self.layers.append(getLayerbyType(layer_type)(**layer))
        except Exception as e:
            raise Exception("Cannot load model at {} wrong format".format(modelPath))


def getModelbyType(model_type) -> _Model:
    if model_type == "gru":
        return GRU_Model
    else:
        raise Exception("Error: Model {} not known.".format(model_type))

def getLayerbyType(layer_type) -> _Layer:
    if layer_type == "gru":
        return GRU_Layer
    elif layer_type == "dense":
        return Dense_Layer
    elif layer_type == "output":
        return Output_Layer
    else:
        raise Exception("Error: Layer {} not known.".format(layer_type))
        