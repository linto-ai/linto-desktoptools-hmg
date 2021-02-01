import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from base import DataSet
from .ui.addfromfolder_ui import Ui_Dialog

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class AddFolderDialog(QtWidgets.QDialog):
    """
    Dialog window to create a new project.
    """
    addSamples = QtCore.pyqtSignal(str, list, name='addSamples')
    def __init__(self, parent, dataset: DataSet):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.dataset = dataset
        self.files = []

        self.populateCB()
        
        self.ui.add_PB.clicked.connect(self.onAddClicked)
        self.ui.browse_PB.clicked.connect(self.onBrowseClicked)
        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.recurs_CB.toggled.connect(self.onRecursToggled)

    def populateCB(self):
        self.ui.keyword_CB.clear()
        for name, label in zip(["non-keyword"] + self.dataset.labels, [None] + self.dataset.labels):
            self.ui.keyword_CB.addItem(name, userData = label)

    def onBrowseClicked(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory")
        if not res:
            return
        self.listSample(res)

    def listSample(self, path):
        self.ui.browse_LE.setText(path)
        self.files = DataSet.listFolder(path, self.ui.recurs_CB.isChecked())
        self.displaydataInfo(len(self.files))

    def displaydataInfo(self, nbFiles: int, nbDuplicate : int = 0):
        self.ui.output_TE.clear()
        info = "File found: {}.\n".format(nbFiles)
        if nbDuplicate > 0:
            info += "Duplicate ignored: {}\n".format(nbDuplicate)
        info += "New files : {}\n".format(nbFiles - nbDuplicate)
        self.ui.output_TE.appendPlainText(info)

    def onRecursToggled(self, state):
        if not self.ui.browse_LE.text().strip() == '':
            self.listSample(self.ui.browse_LE.text())
    
    def onAddClicked(self):
        self.addSamples.emit(self.ui.keyword_CB.currentData(), self.files)
        self.close()




