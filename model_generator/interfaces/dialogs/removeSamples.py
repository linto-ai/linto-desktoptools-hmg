import os

from PyQt5 import QtCore, QtGui, QtWidgets

from base import DataSet
from interfaces.dialogs import SimpleDialog

from .ui.removeSamples_ui import Ui_removeSamples


class RemoveSamplesDialog(QtWidgets.QDialog):
    """
    Dialog window to create a new Dataset.
    """
    on_removed = QtCore.pyqtSignal(name='on_removed')
    def __init__(self, parent, samples: list, datasets : list, parentDataSet: DataSet = None, outputFolder: str = None):
        super().__init__(parent)
        self.ui = Ui_removeSamples()
        self.ui.setupUi(self)

        self.samples = samples
        self.datasets = datasets
        self.parentDataSet = parentDataSet
        self.outputFolder = outputFolder

        self.ui.warning_label.setVisible(False)
        self.ui.nSample_label.setText(str(len(samples)))
        self.ui.removeFromOr_CB.setVisible(parentDataSet is not None)

        # CONNECT
        self.ui.delete_CB.toggled.connect(self.onDeleteCBToggled)
        self.ui.cancel_PB.clicked.connect(self.onCancelClicked)
        self.ui.remove_PB.clicked.connect(self.onRemoveClicked)

    def onDeleteCBToggled(self, state):
        self.ui.warning_label.setVisible(state)

    def onCancelClicked(self):
        self.close()

    def onRemoveClicked(self):
        for dataset in self.datasets:
            dataset.removeSamples(self.samples)
        if self.ui.removeFromOr_CB.isChecked():
            self.parentDataSet.removeSamples(self.samples)
        if self.ui.delete_CB.isChecked():
            for sample in self.samples:
                os.remove(sample.file)
        if self.ui.write_CB.isChecked():
            log_file = os.path.join(self.outputFolder, "removed.txt")
            with open(log_file, "a") as f:
                for sample in self.samples:
                    f.write("{}\n".format(sample.file))
            dialog = SimpleDialog(self, "Done", "{} samples removed.\nRemoved files logged at {}".format(len(self.samples), log_file))
        else:
            dialog = SimpleDialog(self, "Done", "{} samples removed.\nRemoved files logged at {}".format(len(self.samples), log_file))
        dialog.exec_()
        self.on_removed.emit()
        self.close()