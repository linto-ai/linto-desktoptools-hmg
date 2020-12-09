import os
import json

from PyQt5 import QtWidgets, QtCore, QtChart, QtGui

from base import DataSet, Project
from .module import _Module
from interfaces.modules.ui.data_ui import Ui_Form
from interfaces.dialogs.createdialog import CreateDialog
from interfaces.dialogs.deletedataset import DeleteDatasetDialog
from interfaces.dialogs.addFromFolder import AddFolderDialog
from interfaces.dialogs.exportdataset import ExportDatasetDialog
from interfaces.dialogs import SimpleDialog

class Data(_Module):
    moduleTitle= "Data"
    iconName = "data.png"
    shortDescription = ''' Manage your project data '''
    category = "prep"
    moduleHelp = '''
                 The data module allow you to add audio samples to your project.
                 '''

    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project
        self.project.project_updated.connect(self.updateDisplay)
        self.currentDataset = DataSet()
        if(self.project.data["datasets"]):
            self.currentDataset = self.project.getDatasetByName(self.project.data["datasets"][0]["name"])
        
        self.populateDatasetCB()

        #Chart
        self.chart = DataChart(self.currentDataset.datasetValues())
        self.ui.graphPlaceHolder.setLayout(QtWidgets.QHBoxLayout())
        self.ui.graphPlaceHolder.layout().addWidget(self.chart)

        self.updateDisplay()
        
        # CONNECT
        self.ui.createDataSet_PB.clicked.connect(self.onCreateDatasetClicked)
        self.ui.delete_PB.clicked.connect(self.onDeleteDatasetClicked)
        self.ui.currentDataSet_CB.currentTextChanged.connect(self.onDataSetChanged)
        self.ui.addFromFolder_PB.clicked.connect(self.addFromFolder)
        self.currentDataset.dataset_updated.connect(self.updateDisplay)
        self.ui.export_PB.clicked.connect(self.onExportClicked)
        self.ui.import_PB.clicked.connect(self.onImportClicked)

    def updateDisplay(self):
        self.ui.overView_GB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.add_GB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.addFromMan_PB.setEnabled(False) # TODO: implement
        self.ui.export_PB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.overview_TE.clear()
        self.ui.overview_TE.appendPlainText(self.currentDataset.datasetInfo())
        self.chart.updateChart(self.currentDataset.datasetValues())

    def onCreateDatasetClicked(self):
        dialog = CreateDialog(self, self.project.getDatasetNames(), "Create Dataset", "Dataset name:")
        dialog.on_create.connect(self.createNewDataSet)
        dialog.show()

    def onDeleteDatasetClicked(self):
        dialog = DeleteDatasetDialog(self, self.ui.currentDataSet_CB.currentText())
        dialog.on_delete.connect(self.deleteDataset)
        dialog.show()

    def createNewDataSet(self, name: str):
        self.project.addNewDataSet(name)
        self.populateDatasetCB()
        self.ui.currentDataSet_CB.setCurrentText(name)
        self.updateDisplay()

    def deleteDataset(self, name: str):
        self.project.deleteDataSet(name)
        self.populateDatasetCB()
        self.ui.currentDataSet_CB.setCurrentIndex(0)
        self.updateDisplay()

    def populateDatasetCB(self):
        self.ui.currentDataSet_CB.clear()
        for ds in self.project.data["datasets"]:
            self.ui.currentDataSet_CB.addItem(ds["name"], userData = ds["name"])

    def onDataSetChanged(self, name: str):
        if name is not None and name != '':
            self.currentDataset = self.project.getDatasetByName(name)
            self.updateDisplay()
        
    def addFromFolder(self):
        dialog = AddFolderDialog(self, self.currentDataset)
        dialog.addSamples.connect(self.onAddSample)
        dialog.show()
        
    def onAddSample(self, label: str, files: list):
        self.currentDataset.addSampleFiles(label, files)
        self.updateDisplay()

    def onExportClicked(self):
        dialog = ExportDatasetDialog(self, self.currentDataset)
        dialog.show()

    def onImportClicked(self):
        def datasetLabels(manifest):
            target_labels = set()
            for s in manifest:
                target_labels.add(s["label"])
        
            return target_labels
        
        def isMatchingFormat(manifest):
            if type(manifest) != list and type(manifest[0]) != dict:
                return False
            if "label" in manifest[0].keys() and "file" in manifest[0].keys():
                return True
            else:
                return False
        
        def matchAllLabels(target_labels, labels):
            """ The ideal case where all labels in the imported match the project labels"""
            for l in labels + ['']:
                if not l in target_labels:
                    return False
            for l in target_labels:
                if l not in labels + ['']:
                    return False
            return True
                    
        res = QtWidgets.QFileDialog.getOpenFileName(self, "Select dataset json file.", filter="json(*.json)")[0]
        if not res:
            return

        datasetName = os.path.basename(res).split('.')[0]
        with open(res, 'r') as f:
            manifest = json.load(f)
        
        if not isMatchingFormat(manifest):
            dialog = SimpleDialog(self, "Format mismatch", "Could not import from dataset manifest.\nTry using create a new dataset and use import from manifest.")
            dialog.show()
            return
        
        target_labels = datasetLabels(manifest)                   

        if matchAllLabels(target_labels, self.currentDataset.labels):
            if datasetName in self.project.data["datasets"]:
                datasetName += "_imported"
            self.project.addNewDataSet(datasetName)
            dataset = self.project.getDatasetByName(datasetName)
            dataset.importDataSet(res)
            self.populateDatasetCB()
            self.ui.currentDataSet_CB.setCurrentText(datasetName)
            self.updateDisplay()
        else:
            pass
            #TODO label matching
        

class DataChart(QtChart.QChartView):
    def __init__(self, data: list):
        #data: list of tuple (label, value, percent)
        QtChart.QChartView.__init__(self)
        self.pie_slices = [QtChart.QPieSlice("{}- {} ({:.2}%)".format(*d), d[1]) for d in data]

        # Pie chart
        self.pie_series = QtChart.QPieSeries()
        for pie_slice in self.pie_slices:
            self.pie_series.append(pie_slice)
        self.pie_series.setHoleSize(0)

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.chart().layout().setContentsMargins(0,0,0,0)
        self.chart().setMargins(QtCore.QMargins(0,0,0,0))
        self.chart().legend().setAlignment(QtCore.Qt.AlignRight)
        self.chart().addSeries(self.pie_series)

    def updateChart(self, data: list):
        self.pie_series.clear()
        if (sum([d[1] for d in data]) > 0):
            self.pie_slices = [QtChart.QPieSlice("{}- {} ({:.2}%)".format(*d), d[1]) for d in data]
            for pie_slice in self.pie_slices:
                self.pie_series.append(pie_slice)