import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from interfaces.module import _Module

from interfaces.ui.navigation_ui import Ui_Form
from interfaces.data import Data

from scripts.qtutils import CustomButton

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class Navigation(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(_Module, name='clicked')

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project
        self.populate_final()

    def populate_final(self):
        for category in [self.ui.preparationWidget, self.ui.processingWidget, self.ui.processingWidget]:
            category.setLayout(QtWidgets.QHBoxLayout())
            category.layout().addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        modules = [
            Data
        ]
        for module in modules:
            targetWidget = {"prep" : self.ui.preparationWidget, "proc" : self.ui.processingWidget, "output" : self.ui.processingWidget}.get(module.category, "None")
            if targetWidget is None:
                print("Warning: Could not find target for module {}, module ignored".format(module.moduleTitle))
                continue
            instance = module(self.project)
            button = instance.button()
            button.clicked.connect(lambda: self.clicked.emit(instance))
            targetWidget.layout().insertWidget(targetWidget.layout().count() -1 , button) # Insert the widget before the HSpacer
            
            
    def populate(self):
        self.ui.preparationWidget.setLayout(QtWidgets.QHBoxLayout())
        self.ui.preparationWidget.layout().addWidget(CustomButton("Data",
                                                                  "Add and manage data for your project.", 
                                                                  os.path.join(DIR_PATH,"icons/data.png")),1)
        self.ui.preparationWidget.layout().addWidget(CustomButton("Data Augmentation", 
                                                                  "Generate additionnal data for your project", 
                                                                  os.path.join(DIR_PATH,"icons/home.png")),1)
        self.ui.preparationWidget.layout().addWidget(CustomButton("Features", 
                                                                  "Select and customize feature extraction methodology", 
                                                                  os.path.join(DIR_PATH,"icons/home.png")),1)
        
        self.ui.preparationWidget.layout().addWidget(CustomButton("Models", 
                                                                 "Customize Model Parameters", 
                                                                 os.path.join(DIR_PATH,"icons/home.png")),1)

        self.ui.processingWidget.setLayout(QtWidgets.QHBoxLayout())
        
        self.ui.processingWidget.layout().addWidget(CustomButton("Training", 
                                                                 "Train your model", 
                                                                 os.path.join(DIR_PATH,"icons/home.png")),1)

        self.ui.processingWidget.layout().addWidget(CustomButton("Metrics", 
                                                             "Evaluate your model", 
                                                             os.path.join(DIR_PATH,"icons/home.png")),1)
        
        self.ui.processingWidget.layout().addWidget(CustomButton("Reduce False Alarm Rate",
                                                                 "Improve your model by reducing false alarm rate.", 
                                                                 os.path.join(DIR_PATH,"icons/home.png")),1)

        self.ui.outputWidget.setLayout(QtWidgets.QHBoxLayout())
        
        self.ui.outputWidget.layout().addWidget(CustomButton("Test", 
                                                             "Test your model live.", 
                                                             os.path.join(DIR_PATH,"icons/microphone.png")),1)
        self.ui.outputWidget.layout().addWidget(CustomButton("Compare", 
                                                             "Compare your model", 
                                                             os.path.join(DIR_PATH,"icons/home.png")),1)
        self.ui.outputWidget.layout().addWidget(CustomButton("Export", 
                                                             "Export your model", 
                                                             os.path.join(DIR_PATH,"icons/export.png")),1)

    def update(self):
        pass