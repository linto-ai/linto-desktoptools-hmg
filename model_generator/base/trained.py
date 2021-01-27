import json
import os

from base import DataSet
from base.features_param import _Feature
from base.model import _Model

class Trained:
    def __init__(self, name: str):
        self.name = name

        self.trainedFilePath = None

        self.dataset = None
        self.features = None
        self.model = None

        self.isSet = False # If dataset / features / model and set repartition has been set
        self.hasModel = False # If a keras model already exist
        self.isTrained = False # If the model has been trained already

        self.epoch = 0

    def setProfiles(self, dataset: DataSet, features: _Feature, model: _Model, distrib: tuple):
        self.dataset = dataset
        self.features = features
        self.model = model

        train_set, val_set, test_set = self.dataset.formSets(distrib)

        train_set.saveDataSet(self.trainSetPath)
        val_set.saveDataSet(self.valSetPath)
        test_set.saveDataSet(self.testSetPath)

        self.isSet = True
        self.writeTrained()

    def toDict(self) -> dict:
        manifest = dict()
        for key in ["name", "isSet", "hasModel", "isTrained"]:
            manifest[key] = self.__getattribute__(key)
        
        if self.isSet:
            manifest["dataset"] = self.dataset.dataSetName
            manifest["features"] = self.features.name
            manifest["model"] = self.model.name
            manifest["epoch"] = self.epoch
        else:
            for key in ["dataset", "features", "model"]:
                manifest[key] = None

        return manifest

    def writeTrained(self, filePath: str = None):
        if filePath is None:
            if self.trainedFilePath is None:
                raise Exception("No filePath to write Trained model")
            filePath = self.trainedFilePath
        try:
            with open(filePath, 'w') as f:
                json.dump(self.toDict(), f)
        except Exception as e:
            raise Exception(e)
        else:
            self.trainedFilePath = filePath

    def loadTrained(self, project, filePath: str = None,):
        if filePath is None:
            if self.trainedFilePath is None:
                raise Exception("Trained model file not specified")
            filePath = self.trainedFilePath
        try:
            with open(filePath, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            raise Exception(e)
        else:
            self.trainedFilePath = filePath
        
        for key in ["name", "isSet", "hasModel", "epoch", "isTrained"]:
            self.__setattr__(key, manifest.get(key, False))
        
        if self.isSet:
            self.dataset = project.getDatasetByName(manifest["dataset"])
            self.features = project.getFeatures(manifest["features"])
            self.model = project.getModel(manifest["model"])

    def clearTraining(self):
        self.hasModel = False
        self.isTrained = False
        self.epoch = 0
        if os.path.isfile(self.trainedModelPath):
            os.remove(self.trainedModelPath)
        if os.path.isfile(self.logFilePath):
            os.remove(self.logFilePath)
        self.writeTrained()

    def shortDesc(self) -> str:
        """ Return a short description of the trained model """
        return "Dataset : {}\nFeatures: {}\nModel: {}\nEpochs: {}".format(self.dataset.dataSetName, self.features.name, self.model.name, self.epoch)

    def writeManifest(self, filePath: str):
        manifest = dict()
        manifest['acoustic'] = self.features.getAcousticParameters()
        manifest['feature'] = self.features.getParameters()
        manifest['feature']["type"] =self.features.feature_type
        manifest['model'] = dict()
        manifest['model']["inputShape"] = self.features.feature_shape
        manifest['model']["keyword"] = self.dataset.labels

        with open(filePath, 'w') as f:
            json.dump(manifest, f)

    @property
    def folder(self):
        return os.path.dirname(self.trainedFilePath)

    @property
    def trainSetPath(self) -> str:
        return os.path.join(self.folder, "train.json")

    @property
    def valSetPath(self) -> str:
        return os.path.join(self.folder, "val.json")
    
    @property
    def testSetPath(self) -> str:
        return os.path.join(self.folder, "test.json")

    @property
    def trainedModelPath(self) -> str:
        return os.path.join(self.folder, self.name + ".hdf5")

    @property
    def featureFolder(self) -> str:
        return os.path.join(self.folder, "features")
    
    @property
    def logFilePath(self) -> str:
        return os.path.join(self.folder, "logs.txt")