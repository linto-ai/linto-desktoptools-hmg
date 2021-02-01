from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.simpleDialog_ui import Ui_Dialog


class SimpleDialog(QtWidgets.QDialog):
    
    def __init__(self, parent, title : str, message : str):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.ui.label.setText(message)
        self.ui.label.setWordWrap(True)
        self.ui.ok_PB.clicked.connect(self.close)