import os

from PyQt5 import QtCore, QtGui, QtWidgets

from base import DataSet

from .ui.removeFolderSample_ui import Ui_Dialog


class RemoveFolderSamplesDialog(QtWidgets.QDialog):
    """
    Dialog window to create a new Dataset.
    """
    on_removed = QtCore.pyqtSignal(list, name='on_removed')
    def __init__(self, parent, folders: dict):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.folders = folders
        self.currentSamplesSelected = 0
        self.ui.nSamples_label.setText(str(0))
        
        self.populateList()

        # CONNECT
        self.ui.cancel_PB.clicked.connect(self.onCancelClicked)
        self.ui.remove_PB.clicked.connect(self.onRemoveClicked)
        
    def populateList(self):
        for folder in self.folders.keys():
            l_item = QtWidgets.QListWidgetItem()
            l_widget = FolderListItem(folder, self.folders[folder])
            l_widget.checked.connect(self.onCBChecked)
            l_widget.unchecked.connect(self.onCBUnchecked)
            l_item.setSizeHint(l_widget.sizeHint())
            self.ui.list_List.addItem(l_item)
            self.ui.list_List.setItemWidget(l_item, l_widget)

    def onCBUnchecked(self, value):
        self.currentSamplesSelected -= value
        self.ui.nSamples_label.setText(str(self.currentSamplesSelected))

    def onCBChecked(self, value):
        self.currentSamplesSelected += value
        self.ui.nSamples_label.setText(str(self.currentSamplesSelected))

    def onCancelClicked(self):
        self.close()

    def onRemoveClicked(self):
        folders = []
        for i in range(self.ui.list_List.count()):
            item = self.ui.list_List.item(i)
            widget = self.ui.list_List.itemWidget(item)
            if widget.CB.isChecked():
                folders.append(widget.folder)
        self.on_removed.emit(folders)
        self.close()

class FolderListItem(QtWidgets.QWidget):
    checked  = QtCore.pyqtSignal(int, name='on_checked')
    unchecked = QtCore.pyqtSignal(int, name='on_unchecked')
    def __init__(self, folder: str, content: dict):
        QtWidgets.QWidget.__init__(self)
        checkBoxLabel = "{}: ".format(folder)
        for label in content.keys():
                checkBoxLabel += "{} {} samples ".format(content[label], label)
        self.CB = QtWidgets.QCheckBox(checkBoxLabel)
        self.CB.toggled.connect(self.onToggled)
        self.content = content
        self.folder = folder
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.CB)
        self.setLayout(self.layout)
    
    def n_samples(self) -> int:
        return sum(self.content[label] for label in self.content.keys())
    
    def onToggled(self, value):
        if value:
            self.checked.emit(self.n_samples())
        else:
            self.unchecked.emit(self.n_samples())