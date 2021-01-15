from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.createmodel_ui import Ui_Dialog
from interfaces.dialogs import SimpleDialog

class CreateModel(QtWidgets.QDialog):
    """
    Dialog window to create a new Dataset.
    """
    on_create = QtCore.pyqtSignal(str, str, name='on_create')
    def __init__(self, parent, names: list, arch: list):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.names = names
        self.setWindowTitle("Create new model Profile")

        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.create_PB.clicked.connect(self.onCreateClicked)
        self.ui.name_LE.textEdited.connect(self.clearInfo)

        for ds in arch:
            self.ui.model_CB.addItem(ds, userData = ds)
    
    def clearInfo(self, s):
        self.ui.name_LE.setText("")
        self.ui.name_LE.setText(s)
        
    def onCreateClicked(self):
        if self.ui.name_LE.text().strip() == '':
            return
        if self.ui.name_LE.text().strip() in self.names:
            dialog = SimpleDialog(self, "Name taken", "This name already exist")
            dialog.show()
            return
        self.on_create.emit(self.ui.name_LE.text().strip(), self.ui.model_CB.currentText())
        self.close()