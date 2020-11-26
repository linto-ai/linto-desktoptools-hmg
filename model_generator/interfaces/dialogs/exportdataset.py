import os

from PyQt5 import QtCore, QtGui, QtWidgets

from base.dataset_new import DataSet

from .ui.exportdataset_ui import Ui_Dialog


class ExportDatasetDialog(QtWidgets.QDialog):
    """
    Dialog window to create a new Dataset.
    """

    def __init__(self, parent, dataset : DataSet):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.dataset = dataset
        
        self.ui.name_LE.setText(dataset.dataSetName)

        self.targetFolder = None

        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.browse_PB.clicked.connect(self.onBrowseClicked)
        self.ui.export_PB.clicked.connect(self.onExportClicked)
        self.ui.name_LE.textChanged.connect(self.onNameChanged)

    def onExportClicked(self):
        self.setEnabled(False)
        QtWidgets.QApplication.instance().processEvents()
        if os.path.isdir(self.targetFolder):
            self.dataset.progress_notification.connect(self.showProgress)
            self.dataset.exportDataSet(self.ui.name_LE.text(), self.targetFolder, trace=True)
            self.close()
        else:
            self.targetFolder = None
            self.ui.target_location_LE.clear()
            self.ui.export_PB.setEnabled(False)
            self.setEnabled(True)
        
    def showProgress(self, n, tot):
        self.setWindowTitle("Exporting {}/{}".format(n, tot))
        QtWidgets.QApplication.instance().processEvents()

    def onNameChanged(self, name):
        if self.targetFolder is not None:
            self.ui.target_location_LE.setText(os.path.join(self.targetFolder, self.ui.name_LE.text()))
            self.ui.export_PB.setEnabled(len(name) > 0)

    def onBrowseClicked(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a target directory")
        if not res:
            return
        self.targetFolder = res
        self.ui.target_location_LE.setText(os.path.join(res, self.ui.name_LE.text()))
        self.ui.export_PB.setEnabled(len(self.ui.name_LE.text()) > 0)

