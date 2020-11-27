#!/usr/bin/env python3
import os
import sys
import datetime
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module

from base import DataSet, Project
from interfaces.modules.ui.features_ui import Ui_Features
from interfaces.ui.features_chart_ui import Ui_Features_Charts
from interfaces.ui.mfcc_ui import Ui_MFCC
from scripts.qtutils import create_vertical_line, empty_layout

class Features(_Module):
    moduleTitle= "Features"
    iconName = "convert.png"
    shortDescription = ''' Set features configuration '''
    category = "prep"
    moduleHelp = '''
                 The feature module allow you to setup feature extraction parameters for your audio sample.
                 '''
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Features()
        self.ui.setupUi(self)
        self.project = project
        self.features_layout = QtWidgets.QHBoxLayout()
        self.features_changed = False
        self.updateUI()

    def updateUI(self):
        feature_active = not len(self.project.features) == 0
        self.ui.audio_parameters.setEnabled(feature_active)
        self.ui.preprocess.setEnabled(feature_active)
        self.ui.windows.setEnabled(feature_active)
        self.ui.delete_PB.setEnabled(feature_active)
        self.ui.save_PB.setEnabled(self.features_changed)

        