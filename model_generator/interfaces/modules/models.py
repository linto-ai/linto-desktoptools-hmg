import os
import sys
import datetime
import json

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module

from base import Project
from base.model import _Model, _Layer, getLayerbyType, getModelbyType

from interfaces.modules.ui.models_ui import Ui_Form
from interfaces.dialogs import CreateModel, ConfirmDelete, SimpleDialog

from interfaces.utils.qtutils import create_horizontal_spacer, create_vertical_line
from interfaces.utils.assets import getIconPath

class Models(_Module):
    moduleTitle= "Models"
    iconName = "model.png"
    shortDescription = ''' Set model architectures '''
    category = "prep"
    moduleHelp = '''
                 The models module allow you to setup model architectures.
                 '''
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project
        if len(self.project.models) > 0:
            self.currentModel = self.project.getModel(self.project.models[-1])
        else:
            self.currentModel = None

        add_icon = QtGui.QPixmap(getIconPath(__file__, "icons/add.png"))
        self.ui.add_PB.setIcon(QtGui.QIcon(add_icon))
        self.populateModelProfiles()
        self.loadLayerlist()
        self.updateCompileLoss()

        # CONNECT
        self.ui.create_PB.clicked.connect(self.onCreateClicked)
        self.ui.delete_PB.clicked.connect(self.onDeleteClicked)
        self.ui.save_PB.clicked.connect(self.onSaveClicked)
        self.project.model_updated.connect(self.populateModelProfiles)

        self.ui.model_CB.currentTextChanged.connect(self.onProfileChanged)

    def onProfileChanged(self, name):
        if name is not None and name != '':
            self.currentModel = self.project.getModel(name)
            self.loadLayerlist()
        else:
            self.currentModel = None
            self.ui.layerList_List.clear()
        self.updateCompileLoss()

    def updateCompileLoss(self):
        self.ui.optimizer_CB.clear()
        self.ui.loss_CB.clear()
        if self.currentModel is None:
            self.ui.compile_group.setEnabled(False)
        else:
            for o in self.currentModel.allowed_optimizer:
                self.ui.optimizer_CB.addItem(o, userData=o)
            self.ui.optimizer_CB.setCurrentText(self.currentModel.optimizer)
            for l in self.currentModel.allowed_loss_fun:
                self.ui.loss_CB.addItem(l, userData=l)
            self.ui.loss_CB.setCurrentText(self.currentModel.loss)

    def populateModelProfiles(self):
        self.ui.model_CB.clear()
        for model in self.project.models:
            self.ui.model_CB.addItem(model, userData=model)
        if self.ui.model_CB.count() > 0:
            self.ui.model_CB.setCurrentIndex(self.ui.model_CB.count() - 1)
            self.currentModel = self.project.getModel(self.ui.model_CB.currentText())

    def loadLayerlist(self):
        self.ui.layerList_List.clear()
        if self.currentModel is not None:
            for layer in self.currentModel.layers:
                l_item = QtWidgets.QListWidgetItem()
                l_widget = LayerWidget(layer, l_item)
                l_item.setSizeHint(l_widget.sizeHint())
                self.ui.layerList_List.addItem(l_item)
                self.ui.layerList_List.setItemWidget(l_item, l_widget)

    def onCreateClicked(self):
        dialog = CreateModel(self, self.project.models, ["gru"])
        dialog.on_create.connect(self.onModelCreated)
        dialog.show()

    def onModelCreated(self, name: str, arch: str):
        self.currentModel = getModelbyType(arch)(name)
        self.project.addModel(self.currentModel)

    def onDeleteClicked(self):
        dialog = ConfirmDelete(self, "Delete Model Template", "Do you want to delete", self.ui.model_CB.currentText())
        dialog.on_delete.connect(self.deleteModel)
        dialog.show()
    
    def deleteModel(self, name):
        try:
            self.project.deleteModel(name)
        except Exception as e:
            dialog = SimpleDialog(self, "Error", str(e))
            dialog.show()

    def onSaveClicked(self):
        # Fetch layers and layers values in list
        layers = []
        for i in range(self.ui.layerList_List.count()):
            item = self.ui.layerList_List.item(i)
            widget = self.ui.layerList_List.itemWidget(item)
            layer = widget.layer
            values = widget.getAttrs()
            for key in values.keys():
                layer.__setattr__(key, values[key])
            layers.append(layer)
        self.currentModel.layers = layers
        self.currentModel.writeModel()
            

class LayerWidget(QtWidgets.QWidget):
    def __init__(self, layer: _Layer, list_item: QtWidgets.QListWidgetItem):
        QtWidgets.QWidget.__init__(self)
        self.list_item = list_item
        self.layer = layer
        self.custom_attr = dict()
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(50)
        self.layout.addWidget(QtWidgets.QLabel(self.layer.name))

        for elem in self.layer.getEditableParameters():
            self.custom_attr[elem[0]] = None
            if elem[1] is int:
                spinBox = QtWidgets.QSpinBox()
                spinBox.setMinimum(1)
                spinBox.setValue(elem[2])
                self.__setattr__(elem[0], spinBox)
                self.layout.addWidget(QtWidgets.QLabel("{}: ".format(elem[0])))
                self.layout.addWidget(spinBox)
            elif elem[1] is list:
                comboBox = QtWidgets.QComboBox()
                for entry in elem[3]:
                    comboBox.addItem(entry, userData=entry)
                comboBox.setCurrentText(elem[2])
                self.__setattr__(elem[0], comboBox)
                self.layout.addWidget(QtWidgets.QLabel("{}: ".format(elem[0])))
                self.layout.addWidget(comboBox)
            
            elif elem[1] is bool:
                checkBox = QtWidgets.QCheckBox(elem[0])
                checkBox.setChecked(elem[2])
                self.__setattr__(elem[0], checkBox)
                self.layout.addWidget(checkBox)

        self.layout.addSpacerItem(create_horizontal_spacer())

        if not self.layer.is_required:
            self.delete_PB = QtWidgets.QPushButton()
            cancel_icon = QtGui.QPixmap(getIconPath(__file__, "icons/cancel.png"))
            self.delete_PB.setIcon(QtGui.QIcon(cancel_icon))
            self.delete_PB.setIconSize(QtCore.QSize(20,20))
            self.layout.addWidget(self.delete_PB)

        self.setLayout(self.layout)

    def getAttrs(self) -> dict:
        for key in self.custom_attr.keys():
            widget = self.__getattribute__(key)
            if type(widget) is QtWidgets.QSpinBox:
                self.custom_attr[key] = widget.value()
            elif type(widget) is QtWidgets.QComboBox:
                self.custom_attr[key] = widget.currentText()
            elif type(widget) is QtWidgets.QCheckBox:
                self.custom_attr[key] = widget.isChecked()
        return self.custom_attr