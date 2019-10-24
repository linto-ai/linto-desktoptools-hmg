import os
import json
import datetime

from PyQt5 import QtCore

class Project(QtCore.QObject):
    project_updated = QtCore.pyqtSignal(name='project_updated')
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.project_location = ""
        self.project_file = ""
        self.model_path = ""
        self.project_info = dict()
        self.data_info = dict({'set':False})
        self.features_info = dict({'set':False})
        self.model_info = dict({'set':False})
        self.metrics = dict({'set':False})
    
    def open_project(self, project_file):
        self.project_file = project_file
        self.project_location = os.path.dirname(project_file)
        with open(project_file, 'r') as f:
            manifest = json.load(f)
        self.project_info = manifest['general']
        self.data_info = manifest['data']
        self.features_info = manifest['features']
        self.model_info = manifest['model']
        if self.model_info['set']:
            self.model_path = os.path.join(self.project_location, self.project_info['model_name'])
        self.metrics = manifest['metrics']

    def create_project(self, project_name: str, project_location: str, keywords: list, model_name: str):
        self.project_info['project_name'] = project_name
        self.project_location = project_location
        self.project_info['hotwords'] = keywords
        self.project_info['model_name'] = model_name
        self.project_info['creation_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.project_info['last_modification'] = self.project_info['creation_date']

        if not os.path.isdir(project_location):
            os.mkdir(project_location)

        self.project_file = os.path.join(project_location, project_name + ".proj")
        self._write()

    def _write(self):
        self.project_info['last_modification'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        manifest = dict()
        manifest['general'] = self.project_info
        manifest['data'] = self.data_info
        manifest['features'] = self.features_info
        manifest['model'] = self.model_info
        manifest['metrics'] = self.metrics
        
        with open(self.project_file, 'w') as f:
            json.dump(manifest, f)
        
    def _read(self):
        pass

    def update_project(self):
        self._write()
        if self.model_info['set']:
            self.model_path = os.path.join(self.project_location, self.project_info['model_name'])
        self.project_updated.emit()