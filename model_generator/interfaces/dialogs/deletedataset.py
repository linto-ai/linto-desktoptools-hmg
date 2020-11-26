from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.deletedataset_ui import Ui_Dialog


class DeleteDatasetDialog(QtWidgets.QDialog):
    """
    Dialog window to create a new Dataset.
    """
    on_delete = QtCore.pyqtSignal(str, name='on_delete')
    def __init__(self, parent, name):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.name = name
        self.ui.label.setText("Delete dataset: {} ?".format(name))

        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.delete_PB.clicked.connect(self.onDeleteClicked)

    def onDeleteClicked(self):
        self.on_delete.emit(self.name)
        self.close()