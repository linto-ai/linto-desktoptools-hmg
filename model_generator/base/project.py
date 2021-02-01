import os
import json
import datetime
import shutil

from PyQt5 import QtCore
from base import DataSet
from base.features_param import _Feature, getFeaturesByType
from base.model import _Model, getModelbyType
from base.trained import Trained

class Project(QtCore.QObject):
    version = 1.0
    min_version = 1.0

    project_updated = QtCore.pyqtSignal(name='project_updated')
    dataset_updated = QtCore.pyqtSignal(name='dataset_updated')
    feature_updated = QtCore.pyqtSignal(name='feature_updated')
    model_updated = QtCore.pyqtSignal(name='model_updated')
    trained_updated = QtCore.pyqtSignal(name='trained_updated')
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.project_location = ""
        self.project_file = ""
        self.isOpen = False

    ########################################################################
    ##### DATASET
    ########################################################################
    
    def addNewDataSet(self, name):
        self.datasets.append(name)
        dataSetPath = os.path.join(self.project_location, "data", name)
        os.mkdir(dataSetPath)
        os.mkdir(os.path.join(dataSetPath, "features"))
        dataset = DataSet(name, self.keywords)
        dataset.saveDataSet(os.path.join(dataSetPath, name + ".json"))
        self._write()
        self.dataset_updated.emit()

    def deleteDataSet(self, name):
        dataSetPath = os.path.join(self.project_location, "data", name)
        if name in self.datasets:
            usedBy = self.datasetUsedBy(name)
            if len(usedBy) > 0:
                raise Exception("Can't remove dataset. In use by trained models: \n{}".format("-" + "\n-".join(usedBy)))
            self.datasets.remove(name)
            shutil.rmtree(dataSetPath)
            self._write()
            self.dataset_updated.emit()
        else:
            print("Warning: Could not delete dataset {}. Not found".format(name))


    def getDatasetByName(self, name) -> DataSet:
        if name not in self.datasets:
            return None
        dataset = DataSet()
        dataSetPath = os.path.join(self.project_location, "data", name, name+".json")
        dataset.loadDataSet(dataSetPath)
        return dataset

    def addExistingDataSet(self, datasetPath):
        pass

    def datasetUsedBy(self, name) -> list:
        """ Check if features are used in a trained model """
        usedBy = []
        for trainedName in self.trained:
            trained = self.getTrained(trainedName)
            if trained.dataset.dataSetName == name:
                usedBy.append(trainedName)
        return usedBy

    ########################################################################
    ##### FEATURES
    ########################################################################

    def addFeatures(self, features: _Feature):
        self.features.append(features.name)
        featureFile = os.path.join(self.project_location, "features", features.name + ".json")
        with open(featureFile, 'w') as f:
            json.dump(features.generateManifest(), f)
        features.featureFile = featureFile
        self._write()
        self.feature_updated.emit()

    def getFeatures(self, name: str) -> _Feature:
        featureFile = os.path.join(self.project_location, "features", name + ".json")
        with open(featureFile, 'r') as f:
            manifest = json.load(f)
        features = getFeaturesByType(manifest["feature_type"], manifest["name"])
        features.loadValues(manifest)
        features.featureFile = featureFile
        return features

    def deleteFeatures(self, name: str):
        if name in self.features:
            usedBy = self.featuresUsedBy(name)
            if len(usedBy) > 0:
                raise Exception("Can't remove features. In use by trained models: {}".format("-" + "\n-".join(usedBy)))
            featureFile = os.path.join(self.project_location, "features", name +".json")
            try:
                os.remove(featureFile)
            except Exception:
                raise Exception("Could not remove feature profile file: {}".format(e))
            else:
                self.features.remove(name)
                self.update_project()
                self.feature_updated.emit()
    
    def featuresUsedBy(self, name):
        """ Check if features are used in a trained model """
        usedBy = []
        for trainedName in self.trained:
            trained = self.getTrained(trainedName)
            if trained.features.name == name:
                usedBy.append(trainedName)
        return usedBy

    ########################################################################
    ##### MODEL
    ########################################################################
    def addModel(self, model: _Model):
        modelPath = os.path.join(self.project_location, "models", model.name +".json")
        model.modelPath = modelPath
        model.writeModel()
        self.models.append(model.name)
        self.update_project()
        self.model_updated.emit()

    def getModel(self, name: str) -> _Model:
        modelPath = os.path.join(self.project_location, "models", name +".json")
        try:
            with open(modelPath, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            raise e
        model = getModelbyType(manifest["type"])()
        model.loadModel(modelPath)
        model.modelPath = modelPath
        return model

    def deleteModel(self, name: str):
        modelPath = os.path.join(self.project_location, "models", name +".json")
        usedBy = self.modelUsedBy(name)
        if len(usedBy) > 0:
            raise Exception("Can't remove model. In use by trained models: \n{}".format("-" + "\n-".join(usedBy)))
        self.models.remove(name)
        os.remove(modelPath)
        self.update_project()
        self.model_updated.emit()

    def modelUsedBy(self, name):
        """ Check if features are used in a trained model """
        usedBy = []
        for trainedName in self.trained:
            trained = self.getTrained(trainedName)
            if trained.model.name == name:
                usedBy.append(trainedName)
        return usedBy

    ########################################################################
    ##### TRAINED MODELS
    ########################################################################    

    def getTrained(self, name) -> Trained:
        trainedPath = os.path.join(self.project_location, "trained", name, name + ".json")
        trained = Trained(name)
        trained.loadTrained(self, trainedPath)
        return trained

    def addTrained(self, trained: Trained):
        trainedFolder = os.path.join(self.project_location, "trained", trained.name)
        if not os.path.isdir(trainedFolder):
            os.mkdir(trainedFolder)
            os.mkdir(os.path.join(trainedFolder, "features"))
        trainedPath = os.path.join(trainedFolder, trained.name +".json")
        trained.writeTrained(trainedPath)
        self.trained.append(trained.name)
        self._write()
        self.trained_updated.emit()

    def deleteTrained(self, trained : Trained):
        self.trained.remove(trained.name)
        trainedFolder = os.path.join(self.project_location, "trained", trained.name)
        shutil.rmtree(trainedFolder)
        self._write()
        self.trained_updated.emit()

    ########################################################################
    ##### PROJECT
    ########################################################################

    def open_project(self, project_file):
        """
        Open a project, raise Exception if cannot read project file.
        """
        self.project_file = project_file
        self.project_location = os.path.dirname(project_file)
        with open(project_file, 'r') as f:
            manifest = json.load(f)
        try:
            self._check_manifest(manifest)
        except Exception as e:
            raise e

        for key in manifest.keys():
            self.__setattr__(key, manifest[key])

        self.isOpen = True

    def _check_manifest(self, manifest):
        """
        Check version and keys.
        Throw exception if there is something wrong
        """
        try:
            if manifest["project"]["version"] < Project.min_version:
                raise Exception("Project version is too old, please create a new project.")
        except Exception:
                raise Exception("Project version is too old, please create a new project.")
        for entry in ["project", "datasets", "keywords", "features", "models"]:
            if entry not in manifest.keys():
                raise Exception("Missing {} key in manifest.".format(entry))
        # Check nested key ? Maybe later
        

    def create_project(self, project_name: str, project_location: str, keywords: list):
        self.project = dict()
        self.project["name"] = project_name
        self.project["version"] = Project.version

        self.keywords = keywords
        self.datasets = []

        self.features = []
        self.models = []
        self.trained = []
        
        self.project['last_used'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        if not os.path.isdir(project_location):
            os.mkdir(project_location)

        for subFolder in ["data", "models", "features", "trained"]:
            os.mkdir(os.path.join(project_location, subFolder))

        self.project_file = os.path.join(project_location, project_name + ".proj")
        self.project_location = os.path.join(project_location)
        self._write()
        return self

    def _write(self):
        self.project['last_used'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        manifest = {
            "project" : self.project,
            "keywords" : self.keywords,
            "datasets" : self.datasets,
            "features" : self.features,
            "models" : self.models,
            "trained" : self.trained
        }
        with open(self.project_file, 'w') as f:
            json.dump(manifest, f)
        

    def update_project(self):
        self._write()
        self.project_updated.emit()