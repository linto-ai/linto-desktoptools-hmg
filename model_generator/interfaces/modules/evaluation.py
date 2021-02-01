import json

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia

import numpy as np

from .module import _Module
from base import DataSet, Project, Sample
from interfaces.modules.ui.test_ui import Ui_Test
from interfaces.dialogs import RemoveSamplesDialog
from interfaces.utils.assets import getIconPath
from interfaces.utils.qtutils import labeledTextLine, horizontalLine, empty_layout
from processing.files_to_feats import prepare_input_output
from processing.keras_utils import loadModel


class Evaluation(_Module):
    moduleTitle= "Evaluate"
    iconName = "eval.png"
    shortDescription = ''' Evaluate your model '''
    category = "proc"
    moduleHelp = '''
                 Test your model against your test set, evaluate its performances and get metrics.
                 '''
    def __init__(self, project : Project):
        _Module.__init__(self, project)
        self.ui = Ui_Test()
        self.ui.setupUi(self)
        self.project = project
        self.currentProfile = None
        self.table_items = [] #Contain the confusion matrix items 

        self.populateProfiles()
        self.init_conf_table()


        # CONNECT
        self.project.trained_updated.connect(self.populateProfiles)
        self.ui.select_all_CB.toggled.connect(self.onSelectAllToggled)
        self.ui.profile_CB.currentTextChanged.connect(self.onProfileChanged)
        
        ## Buttons
        self.ui.evaluate_PB.clicked.connect(self.onEvaluateClicked)
        self.ui.remove_PB.clicked.connect(self.onRemoveClicked)

    ########################################################################
    ##### UI LOGIC AND UPDATES
    ########################################################################

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
                self.currentProfile = self.project.getTrained(self.ui.profile_CB.currentText())
                self.ui.profile_CB.setToolTip(self.currentProfile.shortDesc())
        else:
            self.currentProfile = None

        
    def onProfileChanged(self, name):
        if self.ui.profile_CB.currentText() != "":
            self.currentProfile = self.project.getTrained(name)
        else:
            self.currentProfile = None
        active = self.currentProfile is not None
        if active:
            self.ui.profile_CB.setToolTip(self.currentProfile.shortDesc())
        else:
            self.ui.profile_CB.setToolTip("")
        self.ui.testSetGroup.setEnabled(active)
        self.ui.evaluate_PB.setEnabled(active)
        self.ui.remove_PB.setEnabled(active)
        self.ui.externalTest_group.setEnabled(active)

    def onEvaluateClicked(self):
        self.ui.evaluate_PB.setEnabled(False)
        self.reset_table()
        self.clearFalseSampleList()
        self.evaluate()
        self.ui.evaluate_PB.setEnabled(True)

    def displayState(self, msg):
        self.ui.progress_Label.setText(msg)
        QtWidgets.QApplication.instance().processEvents()

    def onSelectAllToggled(self, value):
        for i in range(self.ui.false_samples.count()):
            item = self.ui.false_samples.item(i)
            widget = self.ui.false_samples.itemWidget(item)
            layer = widget.CB.setChecked(value)

    def onRemoveClicked(self):
        selectedSamples = []
        for i in range(self.ui.false_samples.count()):
            item = self.ui.false_samples.item(i)
            widget = self.ui.false_samples.itemWidget(item)
            if widget.CB.isChecked():
                selectedSamples.append(widget.sample)
        if len(selectedSamples) == 0:
            return
        testSet = DataSet()
        testSet.loadDataSet(self.currentProfile.testSetPath)

        trainSet = DataSet()
        trainSet.loadDataSet(self.currentProfile.trainSetPath)

        valSet = DataSet()
        valSet.loadDataSet(self.currentProfile.valSetPath)

        dialog = RemoveSamplesDialog(self, selectedSamples,
                                     [testSet, trainSet, valSet],
                                     self.currentProfile.dataset,
                                     outputFolder=self.currentProfile.folder)
        dialog.on_removed.connect(self.onSamplesRemoved)
        dialog.show()

    def onSamplesRemoved(self):
        for i in reversed(range(self.ui.false_samples.count())):
            item = self.ui.false_samples.item(i)
            widget = self.ui.false_samples.itemWidget(item)
            if widget.CB.isChecked():
                self.ui.false_samples.takeItem(i)

    ########################################################################
    ##### TABLE
    ########################################################################
    def init_conf_table(self):
        table = self.ui.conf_mat_table

        table.setRowCount(len(self.project.keywords) + 1) # +1 for non-hotword
        table.setColumnCount(len(self.project.keywords) + 1)
        table.setHorizontalHeaderLabels(['non-hotword'] + self.project.keywords)
        table.setVerticalHeaderLabels(['non-hotword'] + self.project.keywords)
        
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        for r in range(table.rowCount()):
            self.table_items.append([])
            for c in range(table.columnCount()):
                item = QtWidgets.QTableWidgetItem("")
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setData(0,0)
                self.table_items[r].append(item)
                table.setItem(r, c, item)
                if r == c :
                    item.setBackground(QtGui.QColorConstants.Green)
                else:
                    item.setBackground(QtGui.QColorConstants.Gray)


    def setTableValues(self, values):
        for row in range(values.shape[0]):
            for col in range(values.shape[1]):
                 self.table_items[row][col].setText(str(int(values[row][col])))

    def update_table(self):
        for r in self.table_items:
            for item in r:
                item.setText(str(item.data))
    
    def reset_table(self):
         for r in self.table_items:
            for item in r:
                item.setData(0,0)
    
    ########################################################################
    ##### LIST
    ########################################################################
    
    def clearFalseSampleList(self):
        self.ui.false_samples.clear()
    
    def addFalseSample(self, sample: Sample, ct_cp: tuple):
        l_item = QtWidgets.QListWidgetItem()
        l_widget = False_Activations(sample, ct_cp, ['non-hotword'] + self.project.keywords)
        #self.ui.false_samples.append(l_widget)
        l_item.setSizeHint(l_widget.sizeHint())
        self.ui.false_samples.addItem(l_item)
        self.ui.false_samples.setItemWidget(l_item, l_widget)

    ########################################################################
    ##### PROCESSING
    ########################################################################

    def evaluate(self):
        # Data presentation
        evalSet = []
        
        testSet = DataSet()
        testSet.loadDataSet(self.currentProfile.testSetPath)
        evalSet.append(testSet)

        if self.ui.training_set.isChecked():
            trainSet = DataSet()
            trainSet.loadDataSet(self.currentProfile.trainSetPath)
            evalSet.append(trainSet)

        if self.ui.validation_set.isChecked():
            valSet = DataSet()
            valSet.loadDataSet(self.currentProfile.valSetPath)
            evalSet.append(valSet)

        # Feature extraction
        samples, inputs, expectedOutput = prepare_input_output(evalSet, 
                                                                self.currentProfile.features,
                                                                save_features_folder=self.currentProfile.featureFolder,
                                                                traceCallBack=self.displayState,
                                                                returnSamples=True)

        # Load model
        self.displayState("Loading model ...")
        model = loadModel(self.currentProfile.trainedModelPath)

        # Predictions
        self.displayState("Predicting ...")
        predictions = model.predict(inputs)

        # Result classification
        result_matrix = np.zeros((len(evalSet[0].labels) + 1, len(evalSet[0].labels) + 1))
        for sample, prediction, expectedResult in zip(samples, predictions, expectedOutput):
            ct = np.where(expectedResult > 0.0)[0] # Class truth
            if len(ct) == 0:
                ct = 0
            else:
                ct = ct[0] + 1
            triggered = max(prediction) > self.ui.threshold.value()
            if not triggered:
                cp = 0 
            else:
                cp = np.argmax(prediction) + 1 # Class predicted
            result_matrix[ct][cp] += 1
            if ct != cp:
                self.addFalseSample(sample, (ct, cp))

        # Display results
        self.setTableValues(result_matrix)
        self.displayMetrics(result_matrix)

    def displayMetrics(self, result_matrix):
        """Display overall metrics"""
        empty_layout(self.ui.metric_layout)
        n_samples = np.sum(result_matrix)
        self.ui.metric_layout.addWidget(labeledTextLine('Overall accuracy', np.sum(np.diag(result_matrix)), n_samples))
        self.ui.metric_layout.addWidget(labeledTextLine('False negative', np.sum(result_matrix[1:,0]), n_samples - np.sum(result_matrix[0])))
        self.ui.metric_layout.addWidget(labeledTextLine('False positive', n_samples - np.sum(np.diag(result_matrix)) - np.sum(result_matrix[1:,0]), np.sum(result_matrix[0,:])))
        
        hotwords = self.project.keywords
        for i, hw in enumerate(hotwords):
            self.ui.metric_layout.addWidget(horizontalLine())
            self.ui.metric_layout.addWidget(QtWidgets.QLabel(hw))
            self.ui.metric_layout.addWidget(labeledTextLine('Accuracy', result_matrix[i+1, i+1], np.sum(result_matrix[i+1,:])))
            self.ui.metric_layout.addWidget(labeledTextLine('False Negative', np.sum(result_matrix[i+1,:]) - result_matrix[i+1, i+1], np.sum(result_matrix[i+1,:])))
            self.ui.metric_layout.addWidget(labeledTextLine('False Positive', np.sum(result_matrix[:,i+1]) - result_matrix[i+1, i+1], n_samples - np.sum(result_matrix[i+1,:])))

class False_Activations(QtWidgets.QWidget):
    def __init__(self, sample: Sample, ct_cp: tuple, labels: list):
        super().__init__()
        self.sample = sample
        self.sound = QtMultimedia.QSound(self.sample.file)
        layout = QtWidgets.QHBoxLayout()
        self.CB = QtWidgets.QCheckBox(self.sample.file)
        self.CB.setToolTip(self.sample.file)
        label = QtWidgets.QLabel("<font color='red'>{}</font> --> <font color='green'>{}</font>".format(labels[ct_cp[1]], labels[ct_cp[0]]))
        self.play_button = QtWidgets.QPushButton()
        play_icon = QtGui.QPixmap(getIconPath(__file__, "icons/play.png"))
        self.play_button.setIcon(QtGui.QIcon(play_icon))
        self.play_button.setIconSize(QtCore.QSize(20,20))
        layout.addWidget(self.CB)
        layout.addWidget(label)
        layout.addWidget(self.play_button)
        layout.addStretch()
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.setLayout(layout)

        self.play_button.clicked.connect(self.play_audio)

    def play_audio(self):
        self.sound.play()