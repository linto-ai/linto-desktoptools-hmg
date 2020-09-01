from PyQt5 import QtWidgets

from interfaces.module import _Module
from interfaces.ui.data_ui import Ui_Form

class Data(_Module):
    moduleTitle= "Data"
    iconName = "data.png"
    shortDescription = ''' Manage your project data '''
    category = "prep"
    moduleHelp = ''' 
                 The data module allow you to add audio samples to your project.
                 '''

    def __init__(self, project):
        _Module.__init__(self, project)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.project = project

        # CONNECT
        self.ui.setAudio_PB.clicked.connect(self.onSetAudioClicked)

    def loadDataInfo(self):
        if self.project["audio"]["set"]:
            self.ui.audio_GB.setEnabled(False)
            self.ui.overView_GB.setEnabled(True)
            self.ui.add_GB.setEnabled(True)
        
    def onSetAudioClicked(self):
        ask_box = QtWidgets.QMessageBox(self)
        ask_box.setIcon(QtWidgets.QMessageBox.Question)
        ask_box.setText("Set sample rate to {} ? This cannot be changed later.".format(self.ui.sampleRate_SP.value()))
        ask_box.setWindowTitle("Setting Sample Rate")
        ask_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        res = ask_box.exec()
        if res == QtWidgets.QMessageBox.Yes:
            self.project.audio["sampleRate"] = self.ui.sampleRate_SP.value()
            self.project.audio["set"] = True
            self.ui.audio_GB.setEnabled(False)
            self.ui.overView_GB.setEnabled(True)
            self.ui.add_GB.setEnabled(True)
        
    


    