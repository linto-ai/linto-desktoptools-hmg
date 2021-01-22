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
from interfaces.widgets.features_chart import Feature_Chart
from interfaces.utils.qtutils import empty_layout

from interfaces.dialogs import CreateFeature, ConfirmDelete, SimpleDialog

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
        self.initChartWidget()
        self.populateCB()
        self.updateUI()
        self.populateDataSetCB()

        # CONNECT
        self.ui.create_PB.clicked.connect(self.onCreateClicked)
        self.ui.delete_PB.clicked.connect(self.onDeleteClicked)
        self.ui.save_PB.clicked.connect(self.onSaveClicked)
        
        # TODO: Changing current feature doesn't load feature profile
        self.ui.featureProfiles_CB.currentTextChanged.connect(self.onProfileChanged)

        self.ui.sample_rate.valueChanged.connect(self.onValueChanged)
        self.ui.encoding.valueChanged.connect(self.onValueChanged)
        self.ui.sample_t.valueChanged.connect(self.onValueChanged)
        self.ui.preEmp_CB.stateChanged.connect(self.onValueChanged)
        self.ui.preEmp_SB.valueChanged.connect(self.onValueChanged)
        self.ui.window_t_SP.valueChanged.connect(self.onValueChanged)
        self.ui.stride_t_SB.valueChanged.connect(self.onValueChanged)
        self.ui.window_fun_CoB.currentIndexChanged.connect(self.onValueChanged)
        self.ui.analyse_PB.clicked.connect(self.update_chart)

        self.project.dataset_updated.connect(self.populateDataSetCB)
        self.project.feature_updated.connect(self.updateUI)

    def onValueChanged(self, _ = None):
        ''' Enable save button when a value is changed '''
        self.ui.save_PB.setEnabled(True)

    def onProfileChanged(self, name: str):
        if name is not None and name != '':
            self.currentFeatures = self.project.getFeatures(self.ui.featureProfiles_CB.currentText())
            self.updateUI()

    def updateUI(self):
        self.setParameters()
        self.setFeatureWidget()
        self.chartWidget.clearChart()
        feature_active = not len(self.project.features) == 0
        self.ui.audio_parameters.setEnabled(feature_active)
        self.ui.preprocess.setEnabled(feature_active)
        self.ui.windows.setEnabled(feature_active)
        self.ui.delete_PB.setEnabled(feature_active)
        self.ui.analyse_PB.setEnabled(feature_active)
        self.ui.save_PB.setEnabled(False)
    
    def setFeatureWidget(self):
        if self.currentFeatures is not None:
            if self.currentFeaturesWidget is not None:
                empty_layout(self.featureLayout)
                self.currentFeaturesWidget.deleteLater()
            if self.currentFeatures.feature_type == "mfcc":
                self.currentFeaturesWidget = MFCC(self.currentFeatures.getParameters())
                self.currentFeaturesWidget.features_changed.connect(self.onValueChanged)
            self.featureLayout.insertWidget(0, self.currentFeaturesWidget)

    def initChartWidget(self):
        self.chartWidget = Feature_Chart(self.project)
        self.ui.chart_Widget.layout().addWidget(self.chartWidget)

    def populateDataSetCB(self):
        self.chartWidget.clearChart()
        self.ui.dataSet_CB.clear()
        for dataset in self.project.datasets:
            self.ui.dataSet_CB.addItem(dataset, userData=dataset)

    def update_chart(self):
        currentDisplayedFeat = getFeaturesByType(self.currentFeatures.feature_type, "temp")
        currentDisplayedFeat.loadValues(self.paramToDict())
        self.ui.analyse_PB.setEnabled(False)
        self.chartWidget.createGraph(self.project.getDatasetByName(self.ui.dataSet_CB.currentText()),
                                     currentDisplayedFeat, 
                                     self.ui.variance_CB.isChecked())
        self.ui.analyse_PB.setEnabled(False)
        self.ui.analyse_PB.setEnabled(True)

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
            self.ui.window_fun_CoB.setCurrentText(self.currentFeatures.window_fun if self.currentFeatures.window_fun is not None else "none")

    def onCreateClicked(self):
        dialog = CreateFeature(self, self.project.features, ["mfcc"])
        dialog.on_create.connect(self.onFeatureCreated)
        dialog.show()

    def onDeleteClicked(self):
        dialog = ConfirmDelete(self, "Delete Feature Profile", "Do you want to delete", self.ui.featureProfiles_CB.currentText())
        dialog.on_delete.connect(self.deleteProfile)
        dialog.show()

    def deleteProfile(self, name: str):
        try:
            self.project.deleteFeatures(name)
        except Exception as e:
            dialog = SimpleDialog(self, "Cannot delete features", str(e))
            dialog.show()
            return
        self.populateCB()
        self.currentFeatures = None
        if len(self.project.features) == 0:
            self.updateUI()
        else:
            self.ui.featureProfiles_CB.setCurrentIndex(self.ui.featureProfiles_CB.count() -1)
    
    def onFeatureCreated(self, name: str, featType: str):
        features = getFeaturesByType(featType, name)
        self.project.addFeatures(features)
        self.currentFeatures = features
        self.populateCB()
        self.ui.featureProfiles_CB.setCurrentIndex(self.ui.featureProfiles_CB.count() -1)

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
