from PyQt5 import QtCore, QtGui, QtWidgets

class ScrollMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent):
        QtWidgets.QMessageBox.__init__(self, parent)
        self.textArea = QtWidgets.QTextEdit()
        self.textArea.setMinimumSize(300,400)
        self.layout().addWidget(self.textArea)
        
    def setText(self, text):
        self.textArea.setText(text)