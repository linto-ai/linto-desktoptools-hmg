from PyQt5 import QtWidgets

from base.dataset_new import DataSet
from interfaces.module import _Module
from interfaces.ui.data_ui import Ui_Form
from interfaces.dialogs.createdataset import CreateDatasetDialog
from interfaces.dialogs.addFromFolder import AddFolderDialog

class Data(_Module):
    moduleTitle= "Data"
    iconName = "data.png"
    shortDescription = ''' Manage your project data '''
    category = "prep"
    moduleHelp = ''' 
                 The data module allow you to add audio samples to your project.
                 '''

    def __init__(self, project):
        _Module.__init__(self, project)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project
        self.project.project_updated.connect(self.updateDisplay)
        self.currentDataset = DataSet()
        if(self.project.data["datasets"]):
            self.currentDataset = self.project.getDatasetByName(self.project.data["datasets"][0]["name"])

        self.populateDatasetCB()
        self.updateDisplay()
        # CONNECT
        self.ui.setAudio_PB.clicked.connect(self.onSetAudioClicked)
        self.ui.createDataSet_PB.clicked.connect(self.onCreateDatasetClicked)
        self.ui.currentDataSet_CB.currentIndexChanged.connect(self.onDataSetChanged)
        self.ui.addFromFolder_PB.clicked.connect(self.addFromFolder)

    def loadDataInfo(self):
        if self.project["audio"]["set"]:
            self.ui.audio_GB.setEnabled(False)
            self.ui.overView_GB.setEnabled(True)
            self.ui.add_GB.setEnabled(True)

    def updateDisplay(self):
        self.ui.sampleRate_SP.setValue(self.project.audio["sampling_rate"])
        self.ui.audio_GB.setEnabled(not self.project.audio["set"])
        self.ui.overView_GB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.add_GB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.overview_TE.clear()
        self.ui.overview_TE.appendPlainText(self.currentDataset.datasetInfo())
        
    def onSetAudioClicked(self):
        ask_box = QtWidgets.QMessageBox(self)
        ask_box.setIcon(QtWidgets.QMessageBox.Question)
        ask_box.setText("Set sample rate to {} ? This cannot be changed later.".format(self.ui.sampleRate_SP.value()))
        ask_box.setWindowTitle("Setting Sample Rate")
        ask_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        res = ask_box.exec()
        if res == QtWidgets.QMessageBox.Yes:
            self.project.audio["sampleRate"] = self.ui.sampleRate_SP.value()
            self.project.audio["set"] = True
            self.project.update_project()
            self.updateDisplay()

    def onCreateDatasetClicked(self):
        dialog = CreateDatasetDialog(self, self.project.getDatasetNames())
        dialog.on_create.connect(self.createNewDataSet)
        dialog.show()

    def createNewDataSet(self, name: str):
        self.project.addNewDataSet(name)
        self.populateDatasetCB()
        self.updateDisplay()

    def populateDatasetCB(self):
        self.ui.currentDataSet_CB.clear()
        for ds in self.project.data["datasets"]:
            self.ui.currentDataSet_CB.addItem(ds["name"], userData = ds["name"])

    def onDataSetChanged(self, name):
        self.currentDataset = self.project.getDatasetByName(name)
        self.updateDisplay()
        
    
    def addFromFolder(self):
        dialog = AddFolderDialog(self, self.currentDataset)
        dialog.show()

    def onAddSample(self, label, files):
        self.currentDataset


    