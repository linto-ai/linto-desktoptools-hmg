from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.deletedataset_ui import Ui_Dialog


class ConfirmDelete(QtWidgets.QDialog):
    """
    Dialog window to confirm a deletion.
    """
    on_delete = QtCore.pyqtSignal(str, name='on_delete')
    def __init__(self, parent, title: str, message : str, name: str):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.name = name
        self.ui.label.setText("{}: {} ?".format(message, name))

        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.delete_PB.clicked.connect(self.onDeleteClicked)

    def onDeleteClicked(self):
        self.on_delete.emit(self.name)
        self.close()