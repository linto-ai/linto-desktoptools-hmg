#!/usr/bin/env python3
import os
import sys
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from base.project import Project

from interfaces.home import Home
from interfaces.prepare import Prepare
from interfaces.manage import Manage
from interfaces.features import Features
from interfaces.train import Train
from interfaces.test import Test
from interfaces.infere import Infere
from interfaces.export import Export
from interfaces.ui.mainwindow_ui import Ui_MainWindow

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_project = Project()
        self.current_project.project_updated.connect(self.on_project_updated)
        self.load_user_prefs()

        self.home = Home(self.current_project)
        home_layout = QtWidgets.QVBoxLayout()
        home_layout.addWidget(self.home)
        self.ui.home.setLayout(home_layout)

        self.prepare = None
        self.manage = None
        self.features = None
        self.train = None
        self.test = None
        self.infere = None
        self.export = None

        for recent_project in self.user_pref['recent_projects']:
            action = self.ui.menuOpen_Project.addAction(recent_project[0])
            #TODO: Issue Always load last project
            action.triggered.connect(lambda x: self.home.open_project(recent_project[1]))
            
        # Connect
        self.ui.action_open_other.triggered.connect(self.home.open_project)
        self.home.project_openned.connect(self.on_project_open)
        self.home.project_closed.connect(self.close_project)
        self.ui.actionCreate_Project.triggered.connect(self.home._on_create_project)
        
    def on_project_open(self):
        if self.current_project.data_info['set']:
            self.open_manage_tab()
            self.open_features_tab()
        else:
            self.open_prepare_tab()      

        if self.current_project.features_info['set']:    
            self.open_train_tab()
        
        if self.current_project.model_info['set']:
            self.open_test_tab()
            self.open_infere_tab()
            self.open_export_tab()

    def on_project_updated(self):
        if self.current_project.data_info['set']:
            if self.prepare is not None:
                self.prepare.deleteLater()
                self.prepare = None
            self.open_manage_tab()
            self.open_features_tab()
        else:
            self.open_prepare_tab()

        if self.current_project.features_info['set']:    
            self.open_train_tab()
        elif self.train is not None:
            self.train.deleteLater()
            self.train = None
        
        if self.current_project.model_info['set']:
            self.open_test_tab()
            self.open_infere_tab()
            self.open_export_tab()
        else:
            for tab in [self.test, self.infere, self.export]:
                if tab is not None:
                    tab.deleteLater()
                    tab = None

    def close_project(self):
        for tab in [self.prepare, self.manage, self.features, self.train, self.test, self.infere, self.export]:
            if tab is not None:
                tab.deleteLater()
                tab = None

    def on_model_deleted(self):
        for tab in [self.test, self.infere, self.export]:
            if tab is not None:
                tab.deleteLater() 
        self.test = None
        self.infere = None
        self.export = None

    def open_prepare_tab(self):
        if self.prepare is None:
            self.prepare = Prepare(self.current_project)
            self.ui.main_tab.addTab(self.prepare, "Data")

    def open_manage_tab(self):
        if self.manage is None:
            self.manage = Manage(self.current_project)
            self.ui.main_tab.addTab(self.manage, "Manage")

    def open_features_tab(self):
        if self.features is None:
            self.features = Features(self.current_project)
            self.ui.main_tab.addTab(self.features, "Features")

    def open_train_tab(self):
        if self.train is None:
            self.train = Train(self.current_project)
            self.ui.main_tab.addTab(self.train, "Train")
            self.train.train_performed.connect(self.on_project_updated)
            self.train.model_deleted.connect(self.on_model_deleted)
    
    def open_test_tab(self):
        if self.test is None:
            self.test = Test(self.current_project)
            self.ui.main_tab.addTab(self.test, "Evaluate")

    def open_infere_tab(self):
        if self.infere is None:
            self.infere = Infere(self.current_project)
            self.ui.main_tab.addTab(self.infere, "Test")

    def open_export_tab(self):
        if self.export is None:
            self.export = Export(self.current_project)
            self.ui.main_tab.addTab(self.export, "Export")

    def load_user_prefs(self):
        try:
            self.user_pref = json.load(open(os.path.join(DIR_PATH, '.user_preferences.json'), 'r'))
        except:
            self.user_pref = {"last_openned_project" : "",
                                "last_project_parent_folder" : "",
                                "recent_projects" : [],
                                "nmax_recent": 4}
            json.dump(self.user_pref, open(os.path.join(DIR_PATH, '.user_preferences.json'), 'w'))