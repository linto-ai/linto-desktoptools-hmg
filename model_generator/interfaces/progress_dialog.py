from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.progress_dialog_ui import Ui_Dialog

class ProgressDialog(QtWidgets.QDialog):
    def __init__(self, parent, cancel_PB: bool = False):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.cancel_PB.setVisible(cancel_PB)
    
    def set_progress(self, progress):
        self.ui.progressBar.setValue(int(progress))

    def append_text(self, text):
        self.ui.text_output.append(text)