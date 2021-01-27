import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from interfaces.ui.navigation_ui import Ui_Form

from interfaces.modules import _Module
from interfaces.modules import Data, Features, Models, Training, Evaluation, Testing,Export

from interfaces.utils.qtutils import CustomButton

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class Navigation(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal(_Module, name='clicked')
    project_closed = QtCore.pyqtSignal(name='project_closed')

    def __init__(self, project):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project
        self.instanciedModules = []
        self.populate()

        # CONNECT
        self.ui.close_PB.clicked.connect(self.project_closed.emit)

    def populate(self):
        for category in [self.ui.preparationWidget, self.ui.processingWidget, self.ui.outputWidget]:
            category.setLayout(QtWidgets.QHBoxLayout())
            category.layout().addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        modules = [
            Data,
            Features,
            Models,
            Training, 
            Evaluation,
            Testing, 
            Export
        ]
        for module in modules:
            targetWidget = {"prep" : self.ui.preparationWidget, "proc" : self.ui.processingWidget, "output" : self.ui.outputWidget}.get(module.category, "None")
            if targetWidget is None:
                print("Warning: Could not find target for module {}, module ignored".format(module.moduleTitle))
                continue
            instance = module(self.project)
            button = instance.button()
            button.clicked.connect(self.clicked.emit)
            targetWidget.layout().insertWidget(targetWidget.layout().count() -1 , button) # Insert the widget before the HSpacer
            self.instanciedModules.append(instance)

    def onCloseClicked(self):
        pass