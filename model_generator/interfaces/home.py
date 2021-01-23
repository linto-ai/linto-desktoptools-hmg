#!/usr/bin/env python3
import os
import sys
import datetime
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from base import Project
from interfaces.ui.home_ui import Ui_home
from interfaces.utils.qtutils import create_infoline_layout, create_horizontal_line, empty_layout
from interfaces.dialogs import CreateProjectDialog

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class Home(QtWidgets.QWidget):
    project_openned = QtCore.pyqtSignal(Project, name='project_openned')
    def __init__(self, project):
        super().__init__()
        self.ui = Ui_home()
        self.ui.setupUi(self)
        self.project = project
        self.is_openned = False
        self.ui.current_project_box.setVisible(False)
        self.model_graph = None
        self.load_user_prefs()
        
        linagora_icon = QtGui.QPixmap(os.path.join(DIR_PATH, "icons/linagora-labs.png"))
        self.ui.linagora_icon_LB.setPixmap(linagora_icon)

        #Connects
        self.ui.open_project_button.clicked.connect(self._on_open_project)
        self.ui.openprojectbrowsebutton.clicked.connect(self.open_project_prompt)
        
        self.ui.newprojectbrowsebutton.clicked.connect(self.new_project_prompt)
        self.ui.create_project_button.clicked.connect(self._on_create_project)

        self.project_openned.connect(self.on_project_openned)
        
    
    def open_project_prompt(self):
        res = QtWidgets.QFileDialog.getOpenFileName(self, "Select a project file", "/home/rbaraglia/data/hotword/linto_hotwords", "Project file (*.proj)")[0]
        if len(res) != 0:
            self.ui.open_project_string.setText(res)
        return res

    def new_project_prompt(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", "/home/")
        if len(res) != 0:
            if len(self.ui.new_project_name.text()) != 0 and not res.endswith(self.ui.new_project_name.text()):
                res += '/' + self.ui.new_project_name.text()
            self.ui.new_project_location.setText(res)
        return res

    def _on_open_project(self):
        project_path = self.ui.open_project_string.text()
        self.open_project(project_path)

    def open_project(self, file_path):
        if self.is_openned:
            if not self.close_project():
                return
        if type(file_path) is bool or len(file_path) == 0 or not file_path.endswith('.proj'):
            file_path = self.open_project_prompt()
        if len(file_path) == 0:
            return      
        try:
            self.project.open_project(file_path)
        except Exception as err:
            err_box = QtWidgets.QMessageBox(self)
            err_box.setIcon(QtWidgets.QMessageBox.Warning)
            err_box.setText(str(err))
            err_box.setWindowTitle("Manifest error")
            err_box.exec()
        else:
            self.project_openned.emit(self.project)
            self.ui.open_project_string.setText(file_path)
            self.is_openned = True
            
    def _on_create_project(self):
        dialog = CreateProjectDialog(self, self.ui.new_project_name.text(), self.ui.new_project_location.text())
        dialog.show()
        dialog.on_create.connect(self._on_project_created)

    def _on_project_created(self, name, path, hotwords):
        project = self.project.create_project(name, path, hotwords)
        
        #Open newly created project
        self.project_openned.emit(project)
        
    def on_project_openned(self):
        self.update_user_prefs()

    def on_project_closed(self):
        self.is_openned = False
        
    def load_user_prefs(self):
        """ 
        Loads user preferences such as last openned projects.
        """ 
        try:
            self.user_pref = json.load(open(os.path.join(DIR_PATH, '.user_preferences.json'), 'r'))
        except:
            self.user_pref = {"last_openned_project" : "",
                              "last_project_parent_folder" : "",
                              "recent_projects" : [],
                              "nmax_recent": 4}
            json.dump(self.user_pref, open(os.path.join(DIR_PATH, '.user_preferences.json'), 'w'))
        else:
            if self.user_pref['last_openned_project'] != '':
                self.ui.open_project_string.setText(self.user_pref['last_openned_project'])

    def update_user_prefs(self):
        """
        Saves user preferences. 
        """ 
        self.user_pref['last_openned_project'] = self.project.project_file

        if not self.project.project['name'] in [v[0] for v in  self.user_pref['recent_projects']]:
            self.user_pref['recent_projects'].reverse()
            self.user_pref['recent_projects'].append((self.project.project['name'], self.project.project_file))
            self.user_pref['recent_projects'].reverse()
            self.user_pref['recent_projects'] = self.user_pref['recent_projects'][:self.user_pref['nmax_recent']]
        json.dump(self.user_pref, open(os.path.join(DIR_PATH, '.user_preferences.json'), 'w'))

class Graph_rep (QtWidgets.QLabel):
    """
    Create a visual representation of a given model.  
    """
    def __init__(self, project):
        super().__init__()
        self.project = project
        if project.model_info['set']:
            model_path = self.project.model_path
            from scripts.keras_functions import load_model
            from tensorflow.keras.utils import plot_model
            model_dir = os.path.dirname(model_path)
            graph_path = os.path.join(model_dir, 'graph.png')
            plot_model(load_model(model_path), to_file=graph_path, show_shapes=True)
            pixmap = QtGui.QPixmap(graph_path)
            self.setPixmap(pixmap)
        else:
            self.setText("Model haven't been created yet")