from PyQt5 import QtWidgets, QtCore, QtChart, QtGui

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

        #Chart
        self.chart = DataChart(self.currentDataset.datasetValues())
        self.ui.graphPlaceHolder.setLayout(QtWidgets.QHBoxLayout())
        self.ui.graphPlaceHolder.layout().addWidget(self.chart)

        self.updateDisplay()
        
        # CONNECT
        self.ui.createDataSet_PB.clicked.connect(self.onCreateDatasetClicked)
        self.ui.currentDataSet_CB.currentTextChanged.connect(self.onDataSetChanged)
        self.ui.addFromFolder_PB.clicked.connect(self.addFromFolder)
        self.currentDataset.dataset_updated.connect(self.updateDisplay)

    def updateDisplay(self):
        self.ui.overView_GB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.add_GB.setEnabled(len(self.project.data["datasets"]) > 0)
        self.ui.overview_TE.clear()
        self.ui.overview_TE.appendPlainText(self.currentDataset.datasetInfo())
        self.chart.updateChart(self.currentDataset.datasetValues())

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

    def onDataSetChanged(self, name: str):
        self.currentDataset = self.project.getDatasetByName(name)
        self.updateDisplay()
        
    def addFromFolder(self):
        dialog = AddFolderDialog(self, self.currentDataset)
        dialog.addSamples.connect(self.onAddSample)
        dialog.show()
        
    def onAddSample(self, label: str, files: list):
        self.currentDataset.addSampleFiles(label, files)


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