import os
import sys
import datetime
import json
import csv

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module

from base import Project, _Feature, DataSet
from base.model import _Model, _Layer, saveModel
from base.trained import Trained

from interfaces.modules.ui.training_ui import Ui_Form
from interfaces.dialogs import ConfirmDelete, CreateDialog
from interfaces.widgets.training_charts import TrainingChart
from interfaces.utils.qtutils import create_horizontal_spacer, create_vertical_line
from interfaces.utils.assets import getIconPath

from processing.files_to_feats import prepare_input_output
from processing.keras_utils import callbacksDef, loadModel
from processing.training import TrainingSession

class Training(_Module):
    moduleTitle= "Training"
    iconName = "trained.png"
    shortDescription = ''' Train your model '''
    category = "proc"
    moduleHelp = '''
                 Choose your data, your features, your model architecture and train.
                 '''
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project
        self.currentTrained = None
        self.isTraining = False
        self.trainingSession = None
        
        self.setupCharts()

        self.populateProfiles()
        self.onProfileChanged(self.ui.profile_CB.currentText())
        self.populateDataset()
        self.populateFeatures()
        self.populateModels()

        self.updateUI()

        # CONNECT
        ## Project updates
        self.project.dataset_updated.connect(self.populateDataset)
        self.project.feature_updated.connect(self.populateFeatures)
        self.project.model_updated.connect(self.populateModels)
        self.project.trained_updated.connect(self.populateProfiles)

        ## Interface interactivity
        self.ui.profile_CB.currentTextChanged.connect(self.onProfileChanged)
        self.ui.epoch_Radio.toggled.connect(self.epochToggled)

        ## Buttons
        self.ui.new_PB.clicked.connect(self.onCreateClicked)
        self.ui.delete_PB.clicked.connect(self.onDeleteClicked)
        self.ui.set_PB.clicked.connect(self.onSetClicked)
        self.ui.train_PB.clicked.connect(self.onTrainClicked)
        self.ui.stop_PB.clicked.connect(self.onStopClicked)
        self.ui.clear_PB.clicked.connect(self.onClearClicked)

    ########################################################################
    ##### UI LOGIC
    ########################################################################

    def setupCharts(self):
        self.accChart = TrainingChart(["train_acc", "val_acc"])
        self.lossChart = TrainingChart(["train_loss", "val_loss"], bottomToTop=False)
        layout_acc = QtWidgets.QVBoxLayout()
        layout_acc.addWidget(self.accChart)
        self.ui.accGraph_Widget.setLayout(layout_acc)
        layout_loss = QtWidgets.QVBoxLayout()
        layout_loss.addWidget(self.lossChart)
        self.ui.lossGraph_Widget.setLayout(layout_loss)

    def updateUI(self):
        self.updateProfilesGroup()
        self.updateSetGroup()
        self.updateTrainGroup()

    def updateProfilesGroup(self):
        self.ui.delete_PB.setEnabled(self.currentTrained is not None)
        active = self.currentTrained is not None and not self.currentTrained.isSet
        self.ui.dataset_CB.setEnabled(active)
        self.ui.features_CB.setEnabled(active)
        self.ui.model_CB.setEnabled(active)

    def updateSetGroup(self):
        active = self.currentTrained is not None
        for cb in [self.ui.dataset_CB, self.ui.features_CB, self.ui.model_CB]:
            active = active and cb.count() > 0
        self.ui.sets_Group.setEnabled(active)
        if not active:
            return
        editable = active and not self.currentTrained.isSet
        self.ui.trainSet_SB.setEnabled(editable)
        self.ui.valSet_SB.setEnabled(editable)
        self.ui.testSet_SB.setEnabled(editable)
        self.ui.set_PB.setText("Set Profile" if editable else "Change Profile")
    
    def updateTrainGroup(self):
        ready = self.currentTrained is not None and self.currentTrained.isSet
        self.ui.parameters_Group.setEnabled(ready)
        self.ui.train_PB.setEnabled(ready and not self.isTraining)
        self.ui.stop_PB.setEnabled(ready and self.isTraining)

    def populateDataset(self):
        currentdataset = self.ui.dataset_CB.currentText()
        datasets = self.project.datasets
        self.ui.dataset_CB.clear()
        for dataset in datasets:
            self.ui.dataset_CB.addItem(dataset, userData=dataset)
        if currentdataset in datasets:
            self.ui.dataset_CB.setCurrentText(currentdataset)
        else:
            self.updateUI()

    def populateFeatures(self):
        currentFeature = self.ui.features_CB.currentText()
        features = self.project.features
        self.ui.features_CB.clear()
        for feature in features:
            self.ui.features_CB.addItem(feature, userData=feature)
        if currentFeature in features:
            self.ui.features_CB.setCurrentText(currentFeature)
        else:
            self.updateUI()

    def populateModels(self):
        currentModel = self.ui.model_CB.currentText()
        models = self.project.models
        self.ui.model_CB.clear()
        for model in models:
            self.ui.model_CB.addItem(model, userData=model)
        if currentModel in models:
            self.ui.model_CB.setCurrentText(currentModel)
        else:
            self.updateUI()

    def populateProfiles(self):
        current = None
        if self.currentTrained is not None:
            current = self.currentTrained.name
        profiles = self.project.trained
        self.ui.profile_CB.clear()
        for t in profiles:
            self.ui.profile_CB.addItem(t, userData=t)
        if current in profiles:
            self.ui.profile_CB.setCurrentText(current)
        elif len(profiles) > 0:
            self.currentTrained = self.project.getTrained(profiles[-1])
            self.ui.profile_CB.setCurrentText(self.currentTrained.name)
        else:
            self.currentTrained = None
        
    def epochToggled(self, state):
        self.ui.epoch_SB.setEnabled(state)
        self.ui.until_Radio.setChecked(not state)
        self.ui.targetAcc_DSB.setEnabled(not state)
        self.ui.targetScoreSet_DSP.setEnabled(not state)

    def onCreateClicked(self):
        dialog = CreateDialog(self, self.project.trained + ["train", "val", "test"], "Create Training model", "Trained model name:")
        dialog.on_create.connect(self.createNewProfile)
        dialog.show()

    def onSetClicked(self):
        if self.currentTrained.isSet:
            self.changeProfile()
        else:
            self.setupProfile()

    def onDeleteClicked(self):
        dialog = ConfirmDelete(self, "Delete Trained Model", "Do you want to delete", self.ui.profile_CB.currentText())
        dialog.on_delete.connect(self.deleteProfile)
        dialog.show()

    def onProfileChanged(self, name):
        self.accChart.clear()
        self.lossChart.clear()
        self.trainingSession = None
        if name is not None and name != '':
            self.currentTrained = self.project.getTrained(name)
            self.ui.epoch_LCD.display(self.currentTrained.epoch)
            self.displayStatus("Idle")
            self.updateUI()
            if self.currentTrained.isTrained:
                self.loadGraphFromLog()
                self.ui.epoch_LCD.display(self.currentTrained.epoch)

    def onTrainClicked(self):
        self.isTraining = True
        self.updateUI()
        self.train()
        self.isTraining = False
        self.updateUI()

    def onStopClicked(self):
        self.trainingSession.stopTraining()

    def onClearClicked(self):
        self.currentTrained.clearTraining()
        self.onProfileChanged(self.currentTrained.name)

    def updateState(self, msg: str):
        self.ui.state_Label.setText(msg)
        QtWidgets.QApplication.instance().processEvents()

    def loadGraphFromLog(self):
        with open(self.currentTrained.logFilePath, 'r') as f:
            csvreader = csv.reader(f, delimiter=' ')
            rows = [row for row in csvreader]
            epoch = [int(x[0]) for x in rows]
            acc = [float(x[1]) for x in rows]
            val_acc = [float(x[2]) for x in rows]
            loss = [float(x[3]) for x in rows]
            val_loss = [float(x[4]) for x in rows]
            self.accChart.load(((epoch, acc), (epoch, val_acc)))
            self.lossChart.load(((epoch, loss), (epoch, val_loss)))


    ########################################################################
    ##### PROFILE EDITING
    ########################################################################

    def createNewProfile(self, name):
        self.currentTrained = Trained(name)
        self.project.addTrained(self.currentTrained)

    def deleteProfile(self):
        self.project.deleteTrained(self.currentTrained)
    
    def setupProfile(self):
        self.currentTrained.setProfiles(
            self.project.getDatasetByName(self.ui.dataset_CB.currentText()),
            self.project.getFeatures(self.ui.features_CB.currentText()),
            self.project.getModel(self.ui.model_CB.currentText()),
            (self.ui.trainSet_SB.value() / 100, self.ui.valSet_SB.value() / 100, self.ui.testSet_SB.value() / 100)
        )
        self.updateUI()
    
    def changeProfile(self):
        pass

    ########################################################################
    ##### PROCCESSING
    ########################################################################

    def train(self):
        # Training session
        if self.trainingSession == None:
            if self.currentTrained.hasModel:
                model = loadModel(self.currentTrained.trainedModelPath)
            else:
                self.updateState("Creating neural net")
                model = self.currentTrained.model.toKerasModel(self.currentTrained.features.feature_shape, len(self.project.keywords))
                saveModel(model, self.currentTrained.trainedModelPath)
                self.currentTrained.hasModel = True
            self.trainingSession = TrainingSession(model, self.currentTrained.epoch)

        # Set charts ranges
        self.accChart.setRangeX(0, self.trainingSession.epoch + self.ui.epoch_SB.value())
        self.lossChart.setRangeX(0, self.trainingSession.epoch + self.ui.epoch_SB.value())

        # Fetch sets
        trainSet = DataSet()
        trainSet.loadDataSet(self.currentTrained.trainSetPath)

        valSet = DataSet()
        valSet.loadDataSet(self.currentTrained.valSetPath)

        # prepare inputs / outputs
        train_input, train_output = prepare_input_output(trainSet, 
                                                        self.currentTrained.features, 
                                                        traceCallBack=self.updateState, 
                                                        save_features_folder=self.currentTrained.featureFolder)
        val_input, val_output = prepare_input_output(valSet,
                                                     self.currentTrained.features, 
                                                     traceCallBack=self.updateState,
                                                     save_features_folder=self.currentTrained.featureFolder)
        
        # Set callbacks
        callbacks = callbacksDef(self.currentTrained.trainedModelPath, self.train_callback)

        # training
        self.trainingSession.model.fit(train_input, 
                                        train_output,
                                        batch_size=self.ui.batch_SB.value(),
                                        initial_epoch=self.trainingSession.epoch,
                                        epochs= self.trainingSession.epoch + self.ui.epoch_SB.value() + 1,
                                        callbacks=callbacks,
                                        validation_data=(val_input,val_output),
                                        verbose=0,
                                        shuffle=self.ui.shuffle_CB.isChecked())

        self.currentTrained.isTrained = True
        self.currentTrained.epoch = self.trainingSession.epoch
        self.currentTrained.writeTrained()

        # Write training logs
        self.writeLogs()

    def train_callback(self, epoch, logs = {}):
        """ Called during training at the end of each epoch"""
        self.ui.state_Label.setText("Training (Epoch {} / {})...".format(epoch, "x"))
        self.accChart.append(([epoch,logs['accuracy']], [epoch,logs['val_accuracy']]))
        self.lossChart.append(([epoch,logs['loss']], [epoch,logs['val_loss']]))
        self.trainingSession.epoch = epoch
        self.ui.epoch_LCD.display(epoch)
        
        #if self.ui.acc_stop_CB.isChecked() and logs['val_accuracy'] >= self.ui.acc_stop_value_SB.value() / 100.:
            #self.model.stop_training = True
            #self.update_graph_range()

        QtWidgets.QApplication.instance().processEvents() # Refresh UI

    def writeLogs(self):
        acc_values = self.accChart.getValues()
        loss_values = self.lossChart.getValues()
        with open(self.currentTrained.logFilePath, 'w') as f:
            for epoch, acc, val_acc, loss, val_loss in zip(acc_values[0], acc_values[1], acc_values[2], loss_values[1], loss_values[2]):
                f.write("{} {} {} {} {}\n".format(int(epoch), acc, val_acc, loss, val_loss))