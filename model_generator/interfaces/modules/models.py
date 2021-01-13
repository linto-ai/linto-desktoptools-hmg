import os
import sys
import datetime
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module

from base import DataSet, Project, _Feature, getFeaturesByType
from interfaces.modules.ui.models_ui import Ui_Form

from interfaces.dialogs import CreateFeature

class Models(_Module):
    moduleTitle= "Models"
    iconName = "model.png"
    shortDescription = ''' Set model architectures '''
    category = "prep"
    moduleHelp = '''
                 The models module allow you to setup model architectures.
                 '''
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project