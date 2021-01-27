import json

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module
from base import Project, Trained
from interfaces.modules.ui.export import Ui_Export
from interfaces.dialogs import SimpleDialog
from processing.export import *


class Export(_Module):
    moduleTitle= "Export"
    iconName = "export.png"
    shortDescription = ''' Export your trained model '''
    category = "output"
    moduleHelp = '''
                 Convert and export a trained model to different formats.
                 '''
    export_targets = [("Keras (.hdf5)", "keras"), ("Tensorflow Lite (.tflite)", "tflite"), ("TensorflowJS (.json)", "tfjs")]
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Export()
        self.ui.setupUi(self)
        self.project = project
        self.currentProfile = None

        self.populateFormatCB()

        self.populateProfiles()

        # CONNECT
        self.project.trained_updated.connect(self.populateProfiles)
        self.ui.profile_CB.currentTextChanged.connect(self.onProfileChanged)
        self.ui.format_CB.currentIndexChanged.connect(self.onTargetChanged)

        ## Buttons
        self.ui.export_PB.clicked.connect(self.onExportClicked)

    def populateFormatCB(self):
        for title, key in self.export_targets:
            self.ui.format_CB.addItem(title, userData=key)

    def populateProfiles(self):
        current = self.currentProfile.name if self.currentProfile is not None else None
        self.ui.profile_CB.clear()
        profiles = []
        for profile in self.project.trained:
            if self.project.getTrained(profile).isTrained:
                self.ui.profile_CB.addItem(profile, userData=profile)
                profiles.append(profile)
        if len(profiles) > 0 :
            if current is not None and current in profiles:
                self.ui.profile_CB.setCurrentText(current)
            else:
                self.ui.profile_CB.setCurrentIndex(len(profiles) - 1)
                self.setCurrentProfile(self.ui.profile_CB.currentText())
                self.ui.profile_CB.setToolTip(self.currentProfile.shortDesc())
        else:
            self.currentProfile = None
            self.ui.export_PB.setEnabled(False)

    def onProfileChanged(self, name):
        if self.ui.profile_CB.currentText() != "":
            self.setCurrentProfile(name)
        else:
            self.currentProfile = None

        active = self.currentProfile is not None
        self.ui.export_PB.setEnabled(active)
        self.ui.format_CB.setEnabled(active)

    def onTargetChanged(self, index):
        target = self.ui.format_CB.itemData(index)
        comp = True
        reason = ""
        if target == "tflite":
            comp, reason = isTFLiteCompatible(self.currentProfile.model)
        elif target == "tfjs":
            comp, reason = isTFJSCompatible(self.currentProfile.model)
        self.ui.export_PB.setEnabled(comp)
        self.ui.compatibility_label.setText(reason)

    def setCurrentProfile(self, name):
        self.currentProfile = self.project.getTrained(name)
        self.ui.profile_CB.setToolTip(self.currentProfile.shortDesc())

    def onExportClicked(self):
        target = self.ui.format_CB.itemData(self.ui.format_CB.currentIndex())
        if target == "keras":
            ext = ".hdf5"
        elif target == "tflite":
            ext = ".tflite"
        elif target == "tfjs":
            ext = ".json"

        file_path = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         "Export Model",
                                                          os.path.join(self.project.project_location, self.currentProfile.name + ext),
                                                           "{} File (*.{})".format(target, ext))[0]
        if not file_path:
            return
        target_folder = os.path.dirname(file_path)
        try:
            if target == "keras":
                exportKeras(self.currentProfile.trainedModelPath, file_path)
            elif target == "tflite":
                exportTFLite(self.currentProfile.trainedModelPath, file_path)
            elif target == "tfjs":
                exportName = os.path.splitext(os.path.basename(file_path))[0]
                target_folder = os.path.join(os.path.dirname(file_path), exportName)
                exportTFJS(self.currentProfile.trainedModelPath, target_folder)
        except Exception as e:
            dialog = SimpleDialog(self, "Failed to export", str(e))
            return
    
        if self.ui.features_CkB.isChecked():
           targetManifest = os.path.join(target_folder, "model_parameters.json") 
           self.currentProfile.writeManifest(targetManifest)

        dialog = SimpleDialog(self, "Model Exported !", "Model exported at {}".format(file_path if target is not "tfjs" else target_folder))
        dialog.show()