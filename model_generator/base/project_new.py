import os
import json
import datetime
import shutil

from PyQt5 import QtCore
from base import DataSet
from base.features_param import _Feature, getFeaturesByType
from base.model import _Model, getModelbyType

class Project(QtCore.QObject):
    version = 1.0
    min_version = 1.0

    project_updated = QtCore.pyqtSignal(name='project_updated')
    dataset_updated = QtCore.pyqtSignal(name='dataset_updated')
    feature_updated = QtCore.pyqtSignal(name='feature_updated')
    model_updated = QtCore.pyqtSignal(name='model_updated')
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.project_location = ""
        self.project_file = ""
        self.isOpen = False

    ########################################################################
    ##### DATASET
    ########################################################################
    
    def addNewDataSet(self, name):
        self.data["datasets"].append({"name" : name})
        dataSetPath = os.path.join(self.project_location, "data", name)
        os.mkdir(dataSetPath)
        os.mkdir(os.path.join(dataSetPath, "features"))
        dataset = DataSet(name, self.data["keywords"])
        dataset.saveDataSet(os.path.join(dataSetPath, name + ".json"))
        self._write()
        self.dataset_updated.emit()

    def deleteDataSet(self, name):
        dataSetPath = os.path.join(self.project_location, "data", name)
        index = None
        for i, ds in enumerate(self.data["datasets"]):
            if ds['name'] == name:
                index = i
                break
        if index is not None:
            self.data["datasets"].pop(index)
            shutil.rmtree(dataSetPath)
            self._write()
            self.dataset_updated.emit()
        else:
            print("Warning: Could not delete dataset {}. Not found".format(name))

    def getDatasetNames(self) -> list:
        return [ds["name"] for ds in self.data["datasets"]]

    def getDatasetByName(self, name) -> DataSet:
        if name not in self.getDatasetNames():
            return None
        dataset = DataSet()
        dataSetPath = os.path.join(self.project_location, "data", name, name+".json")
        dataset.loadDataSet(dataSetPath)
        return dataset

    def addExistingDataSet(self, datasetPath):
        pass

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
            featureFile = os.path.join(self.project_location, "features", name +".json")
            try:
                os.remove(featureFile)
            except Exception:
                raise Exception("Could not remove feature profile")
            else:
                self.features.remove(name)
                self.update_project()
                self.feature_updated.emit()
        
        
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
        self.models.remove(name)
        os.remove(modelPath)
        self.update_project()
        self.model_updated.emit()

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
        for entry in ["project", "data", "features", "models"]:
            if entry not in manifest.keys():
                raise Exception("Missing {} key in manifest.".format(entry))
        # Check nested key ? Maybe later
        

    def create_project(self, project_name: str, project_location: str, keywords: list):
        self.project = dict()
        self.project["name"] = project_name
        self.project["version"] = Project.version

        self.data = dict()
        self.data["keywords"] = keywords
        self.data["datasets"] = []

        self.features = []
        self.models = []
        
        self.project['last_used'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        if not os.path.isdir(project_location):
            os.mkdir(project_location)

        for subFolder in ["data", "models","features", "outputs"]:
            os.mkdir(os.path.join(project_location, subFolder))

        self.project_file = os.path.join(project_location, project_name + ".proj")
        self.project_location = os.path.join(project_location)
        self._write()
        return self

    def _write(self):
        self.project['last_used'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        manifest = {
            "project" : self.project,
            "data" : self.data,
            "features" : self.features,
            "models" : self.models
        }
        with open(self.project_file, 'w') as f:
            json.dump(manifest, f)
        

    def update_project(self):
        self._write()
        self.project_updated.emit()