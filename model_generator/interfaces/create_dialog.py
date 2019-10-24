import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from .ui.create_dialog_ui import Ui_Dialog

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class CreateDialog(QtWidgets.QDialog):
    on_create = QtCore.pyqtSignal(str, str, str, list, name='on_create_clicked')
    def __init__(self, parent, project_name: str, project_path):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        if project_name != '':
            self.ui.name_LE.setText(project_name)
            self.ui.model_name_LE.setText(project_name)
        
        if project_path != '':
            self.ui.location_LE.setText(project_path)
        
        self.add_element()

        #Connect
        self.ui.add_Button.clicked.connect(self.add_element)
        self.ui.create_PB.clicked.connect(self.on_create_clicked)
        self.ui.cancel_PB.clicked.connect(self.close)
        self.ui.locationChange_PB.clicked.connect(self.on_change_clicked)
        self.ui.name_LE.textEdited.connect(self.ui.model_name_LE.setText)
    
    def on_change_clicked(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", "/home/")
        if len(res) != 0:
            if len(self.ui.name_LE.text()) != 0 and not res.endswith(self.ui.name_LE.text()):
                res += '/' + self.ui.name_LE.text()
            self.ui.location_LE.setText(res)

    def add_element(self):
        l_item = QtWidgets.QListWidgetItem()
        l_widget = Activation_Sample("hotword_{}".format(self.ui.hotwords_Widget.count()), l_item)
        l_widget.deleted.connect(self.delete_element)
        l_item.setSizeHint(l_widget.sizeHint())
        self.ui.hotwords_Widget.addItem(l_item)
        self.ui.hotwords_Widget.setItemWidget(l_item, l_widget)

    def delete_element(self, item):
        if self.ui.hotwords_Widget.count() > 1:
            self.ui.hotwords_Widget.takeItem(self.ui.hotwords_Widget.row(item))

    def on_create_clicked(self):
        warning_box = QtWidgets.QMessageBox(self)
        warning_box.setIcon(QtWidgets.QMessageBox.Warning)
        warning_box.setWindowTitle("Warning")
        warning_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

        if self.ui.name_LE.text().strip() == '':
            warning_box.setText("A project needs a name")
            warning_box.exec()
            return
        
        if self.ui.model_name_LE.text().strip() == '':
            warning_box.setText("A model needs a name")
            warning_box.exec()
            return

        if not os.path.isdir(os.path.dirname(self.ui.location_LE.text())):
            warning_box.setText("Could not find folder {}".format(self.ui.location_LE.text()))
            warning_box.exec()
            return

        hw_list = []
        for i in range(self.ui.hotwords_Widget.count()):
            item = self.ui.hotwords_Widget.item(i)
            hw_list.append(self.ui.hotwords_Widget.itemWidget(item).name)
        print(hw_list)
        self.on_create.emit(self.ui.name_LE.text(), self.ui.location_LE.text(),  self.ui.model_name_LE.text(), hw_list)
        self.close()
        
class Activation_Sample(QtWidgets.QWidget):
    deleted = QtCore.pyqtSignal(QtWidgets.QListWidgetItem, name='deleted')
    def __init__(self, basename: str, list_item):
        QtWidgets.QWidget.__init__(self)
        self.list_item = list_item
        self._name = basename
        self.lineEdit = QtWidgets.QLineEdit(basename)
        self.delete_PB = QtWidgets.QPushButton()
        cancel_icon = QtGui.QPixmap("{}/icons/cancel.png".format(DIR_PATH))
        self.delete_PB.setIcon(QtGui.QIcon(cancel_icon))
        self.delete_PB.setIconSize(QtCore.QSize(20,20))

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.delete_PB)
        self.setLayout(layout)

        #Connect
        self.delete_PB.clicked.connect(self.on_delete_clicked)
        self.lineEdit.editingFinished.connect(self.on_name_edit)

    def on_name_edit(self):
        self.name=self.lineEdit.text()

    def on_delete_clicked(self):
        self.deleted.emit(self.list_item)

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name: str):
        self._name = name.strip().replace(' ', '_').lower()
        if self._name != name:
            self.lineEdit.setText(self._name)