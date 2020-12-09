#!/usr/bin/env python3
import os
import sys
import datetime
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module

from base import DataSet, Project, _Feature, getFeaturesByType
from interfaces.modules.ui.features_ui import Ui_Features
from interfaces.ui.features_chart_ui import Ui_Features_Charts
from interfaces.ui.mfcc_ui import Ui_MFCC
from interfaces.widgets.features_widgets import MFCC

from interfaces.dialogs import CreateFeature

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
        self.currentFeatures = self.project.getFeatures(self.project.features[-1]) if len(self.project.features) > 0 else None
        self.features_layout = QtWidgets.QHBoxLayout()
        
        self.featureLayout = QtWidgets.QVBoxLayout()
        self.ui.feature_Widget.setLayout(self.featureLayout)
        self.currentFeaturesWidget = None
        self.updateUI()
        self.setParameters()

        # CONNECT
        self.ui.create_PB.clicked.connect(self.onCreateClicked)
        self.ui.save_PB.clicked.connect(self.onSaveClicked)
        #self.ui.featureProfiles_CB.currentTextChanged

        self.ui.sample_rate.valueChanged.connect(self.onValueChanged)
        self.ui.encoding.valueChanged.connect(self.onValueChanged)
        self.ui.sample_t.valueChanged.connect(self.onValueChanged)
        self.ui.preEmp_CB.stateChanged.connect(self.onValueChanged)
        self.ui.preEmp_SB.valueChanged.connect(self.onValueChanged)
        self.ui.window_t_SP.valueChanged.connect(self.onValueChanged)
        self.ui.stride_t_SB.valueChanged.connect(self.onValueChanged)
        self.ui.window_fun_CoB.currentIndexChanged.connect(self.onValueChanged)

    def onValueChanged(self, _ = None):
        self.ui.save_PB.setEnabled(True)

    def updateUI(self):
        self.populateCB()
        self.setParameters()
        self.setFeatureWidget()
        feature_active = not len(self.project.features) == 0
        self.ui.audio_parameters.setEnabled(feature_active)
        self.ui.preprocess.setEnabled(feature_active)
        self.ui.windows.setEnabled(feature_active)
        self.ui.delete_PB.setEnabled(feature_active)
        self.ui.save_PB.setEnabled(False)
    
    def setFeatureWidget(self):
        if self.currentFeatures is not None:
            if self.currentFeaturesWidget is not None:
                self.featureLayout.removeWidget(self.currentFeaturesWidget)
            if self.currentFeatures.feature_type == "mfcc":
                self.currentFeaturesWidget = MFCC(self.currentFeatures.getParameters())
                self.currentFeaturesWidget.features_changed.connect(self.onValueChanged)
            self.featureLayout.insertWidget(0, self.currentFeaturesWidget)

    def populateCB(self):
        self.ui.featureProfiles_CB.clear()
        for feat in self.project.features:
            self.ui.featureProfiles_CB.addItem(feat, userData=feat)
    
    def setParameters(self):
        if self.currentFeatures:
            self.ui.sample_rate.setValue(self.currentFeatures.sample_rate)
            self.ui.encoding.setValue(self.currentFeatures.encoding)
            self.ui.sample_t.setValue(self.currentFeatures.sample_length)
            self.ui.preEmp_CB.setChecked(self.currentFeatures.use_emphasis)
            self.ui.preEmp_SB.setValue(self.currentFeatures.emphasis_factor)
            self.ui.window_t_SP.setValue(self.currentFeatures.window_length)
            self.ui.stride_t_SB.setValue(self.currentFeatures.window_stride)
            self.ui.window_fun_CoB.setCurrentText(self.currentFeatures.window_fun)

    def onCreateClicked(self):
        dialog = CreateFeature(self, self.project.features, ["mfcc"])
        dialog.on_create.connect(self.onFeatureCreated)
        dialog.show()
    
    def onFeatureCreated(self, name: str, featType: str):
        features = getFeaturesByType(featType, name)
        self.project.addFeatures(features)
        self.currentFeatures = features
        self.updateUI()

    def onSaveClicked(self):
        self.currentFeatures.loadValues(self.paramToDict())
        self.currentFeatures.write()
        self.ui.save_PB.setEnabled(False)
    
    def paramToDict(self) -> dict:
        acoustic = dict()
        acoustic["sample_rate"] = self.ui.sample_rate.value()
        acoustic["encoding"] = self.ui.encoding.value()
        acoustic["sample_length"] = self.ui.sample_t.value()
        acoustic["use_emphasis"] = self.ui.preEmp_CB.isChecked()
        acoustic["emphasis_factor"] = self.ui.preEmp_SB.value()
        acoustic["window_length"] = self.ui.window_t_SP.value()
        acoustic["window_stride"] = self.ui.stride_t_SB.value()
        acoustic["window_fun"] = self.ui.window_fun_CoB.currentText()

        acoustic = {**acoustic, **self.currentFeaturesWidget.getValues()}

        return acoustic
