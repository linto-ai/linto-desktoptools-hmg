import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets, QtChart

from base.project import Project
from scripts.qtutils import CustomButton

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class _Module(QtWidgets.QWidget):
    moduleTitle= ""
    iconName = ""
    category = ""
    shortDescription = ''' '''
    moduleHelp = ''' '''

    newStatus = QtCore.pyqtSignal(str, int, name='newStatus')
    
    def __init__(self, project):
        QtWidgets.QWidget.__init__(self)
        self.project = project
    
    @classmethod
    def button(cls) -> QtWidgets.QWidget:
        return CustomButton(cls.moduleTitle, cls.shortDescription, os.path.join(DIR_PATH, "icons", cls.iconName))

    @classmethod
    def icon(cls) -> QtWidgets:
        pushButton = QtWidgets.QPushButton()
        iconMap = QtGui.QPixmap(os.path.join(DIR_PATH, "icons", cls.iconName))
        pushButton.setIcon(QtGui.QIcon(iconMap))
        pushButton.setIconSize(QtCore.QSize(50,50))
        pushButton.setToolTip(cls.shortDescription)
        return pushButton

    def displayStatus(self, message: str, timeout: int = 0):
        self.newStatus.emit(message, timeout)



