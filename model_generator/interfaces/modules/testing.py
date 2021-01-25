import json

from PyQt5 import QtCore, QtGui, QtWidgets

from .module import _Module
from base import Project, Trained
from interfaces.modules.ui.testing_ui import Ui_Infere
from interfaces.widgets.infere_chart import InfereChart
from processing.inference_engine import InferenceEngine
from interfaces.utils.assets import getIconPath


class Testing(_Module):
    moduleTitle= "Testing"
    iconName = "microphone.png"
    shortDescription = ''' Try your trained model '''
    category = "output"
    moduleHelp = '''
                 Test your trained model with your microphone.
                 '''
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Infere()
        self.ui.setupUi(self)
        self.project = project
        self.currentProfile = None

        self.isRunning = False
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)

        self.init_chart()
        self.populateProfiles()
        
        # CONNECT
        self.project.trained_updated.connect(self.populateProfiles)
        self.ui.threshold.valueChanged.connect(self.onThresholdChanged)
        self.timer.timeout.connect(self.onTimerTimeout)

        ## Buttons
        self.ui.test_PB.clicked.connect(self.onTestClicked)

    def init_chart(self):
        self.chart = InfereChart(self.project.keywords, self.ui.threshold.value())
        graph_layout = QtWidgets.QHBoxLayout()
        graph_layout.addWidget(self.chart)
        self.ui.graph_placeholder.setLayout(graph_layout)

    def populateProfiles(self):
        current = self.currentProfile.name if self.currentProfile is not None else None
        self.ui.profile_CB.clear()
        profiles = []
        for profile in self.project.trained:
            if self.project.getTrained(profile).isTrained:
                self.ui.profile_CB.addItem(profile, userData=profile)
                profiles.append(profile)
        if len(profiles) > 0 :
            if current is not None and current in profiles:
                self.ui.profile_CB.setCurrentText(current)
            else:
                self.ui.profile_CB.setCurrentIndex(len(profiles) - 1)
                self.setCurrentProfile(self.ui.profile_CB.currentText())
                self.ui.profile_CB.setToolTip(self.currentProfile.shortDesc())
        else:
            self.currentProfile = None
            self.ui.test_PB.setEnabled(False)

    def onProfileChanged(self, name):
        if self.ui.profile_CB.currentText() != "":
            self.setCurrentProfile(name)
        else:
            self.currentProfile = None
            self.ui.test_PB.setEnabled(False)
        active = self.currentProfile is not None
        self.ui.profile_CB.setToolTip(self.currentProfile.shortDesc())
        self.ui.test_PB.setEnabled(active)

    def setCurrentProfile(self, name):
        self.currentProfile = self.project.getTrained(name)
        self.chart.clear()
        self.inferenceEngine = InferenceEngine(self.currentProfile.features, self.currentProfile.trainedModelPath, self.ui.threshold.value())
        self.inferenceEngine.prediction.connect(self.chart.addValue)
        self.inferenceEngine.sample_detected.connect(self.onActivationSamples)
        self.ui.test_PB.setEnabled(True)

    def onTestClicked(self):
        if self.isRunning:
            self.inferenceEngine.stopInference()
            self.ui.test_PB.setText("Start")
            self.isRunning = False
        else:
            self.chart.clear()
            self.inferenceEngine.startInference()
            self.ui.test_PB.setText("Stop")
            self.isRunning = True

    def onThresholdChanged(self, value):
        self.chart.setThreshold(value)
        if self.inferenceEngine is not None:
            self.inferenceEngine.threshold = value

    def onActivationSamples(self, signal, cp):
        self.ui.detected_label.setText(self.project.keywords[cp])
        if self.timer.isActive:
            self.timer.stop()
        self.timer.start(1000)
        self.add_activated_sample(signal, cp)

    def add_activated_sample(self, data: bytes, cp: int):
        l_item = QtWidgets.QListWidgetItem()
        l_widget = Activation_Sample(data, cp, ['non-hotword'] + self.project.keywords, l_item)
        l_widget.deleted.connect(self.remove_activated_sample)
        l_item.setSizeHint(l_widget.sizeHint())
        
        self.ui.activation_list.addItem(l_item)
        self.ui.activation_list.setItemWidget(l_item, l_widget)

    def remove_activated_sample(self, item):
        self.ui.activation_list.takeItem(self.ui.activation_list.row(item))

    def onTimerTimeout(self):
        self.ui.detected_label.setText("...")

class Activation_Sample(QtWidgets.QWidget):
    deleted = QtCore.pyqtSignal(QtWidgets.QListWidgetItem, name='deleted')
    def __init__(self, data: "Audio data", cp: "Activated class", labels: "hotword list", list_item):
        super().__init__()
        self.list_item = list_item
        
        self.data = data
        self.cp = cp
        self.CB = QtWidgets.QCheckBox(labels[self.cp])
        self.play_PB = QtWidgets.QPushButton()
        play_icon = QtGui.QPixmap(getIconPath(__file__, "icons/play.png"))
        self.play_PB.setIcon(QtGui.QIcon(play_icon))
        self.play_PB.setIconSize(QtCore.QSize(20,20))
        self.delete_PB = QtWidgets.QPushButton()
        cancel_icon = QtGui.QPixmap(getIconPath(__file__, "icons/cancel.png"))
        self.delete_PB.setIcon(QtGui.QIcon(cancel_icon))
        self.delete_PB.setIconSize(QtCore.QSize(20,20))
        self.hotword_CB = QtWidgets.QComboBox()
        for c in labels:
            self.hotword_CB.addItem(c)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.CB)
        layout.addWidget(self.play_PB)
        layout.addWidget(self.hotword_CB)
        layout.addWidget(self.delete_PB)
        layout.addStretch()
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)
        
        self.play_PB.clicked.connect(self.play_sample)
        self.delete_PB.clicked.connect(self.delete)

    def play_sample(self):
        pass 
        #self.player.play_from_buffer(self.data)

    def delete(self):
        self.deleted.emit(self.list_item)