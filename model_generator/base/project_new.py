import os
import json
import datetime
import shutil

from PyQt5 import QtCore
from base.dataset_new import DataSet

class Project(QtCore.QObject):
    version = 1.0
    min_version = 1.0

    project_updated = QtCore.pyqtSignal(name='project_updated')
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
        for entry in ["project", "data", "audio", "models"]:
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

        self.audio = dict()
        self.audio["sampling_rate"] = 16000
        self.audio["encoding"] = 2
        self.audio["set"] = False

        self.models = []
        
        self.project['last_used'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        if not os.path.isdir(project_location):
            os.mkdir(project_location)

        for subFolder in ["data", "models", "outputs"]:
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
            "audio" : self.audio,
            "models" : self.models
        }
        with open(self.project_file, 'w') as f:
            json.dump(manifest, f)
        

    def update_project(self):
        self._write()
        self.project_updated.emit()