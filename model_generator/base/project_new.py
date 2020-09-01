import os
import json
import datetime

from PyQt5 import QtCore

class Project(QtCore.QObject):
    version = 1.0
    min_version = 1.0

    project_updated = QtCore.pyqtSignal(name='project_updated')
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.project_location = ""
        self.project_file = ""
        self.isOpen = False
    
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
        self._write()

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