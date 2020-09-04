from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.createdataset_ui import Ui_Dialog


class CreateDatasetDialog(QtWidgets.QDialog):
    """
    Dialog window to create a new Dataset.
    """
    on_create = QtCore.pyqtSignal(str, name='on_create')
    def __init__(self, parent, names):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.names = names

        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.create_PB.clicked.connect(self.onCreateClicked)
        self.ui.name_LE.textEdited.connect(self.clearInfo)
    
    def clearInfo(self, s):
        self.ui.name_LE.setText("")
        self.ui.name_LE.setText(s)

    def onCreateClicked(self):
        if self.ui.name_LE.text().strip() == '':
            return
        if self.ui.name_LE.text().strip() in self.names:
            self.ui.info_Label.setText("This Dataset name already exist")
            return
        self.on_create.emit(self.ui.name_LE.text().strip())
        self.close()