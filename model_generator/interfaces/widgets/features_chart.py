from PyQt5 import QtWidgets, QtCore
from base import Project, _Feature

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from processing.files_to_feats import files_to_feat
from interfaces.utils.qtutils import empty_layout
import numpy as np

class Feature_Chart(QtWidgets.QWidget):
    def __init__(self, project: Project):
        QtWidgets.QWidget.__init__(self)
        self.project = project
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

    def createGraph(self, dataSet, feature_param : _Feature, display_variance):
        
        empty_layout(self.layout)
        self.figure = Figure()
        self.figure.clear()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        hotwords = self.project.data["keywords"]
        n_graph = 1 + display_variance

        for i, hotword in enumerate(hotwords):
            axes = self.figure.add_subplot(len(hotwords),n_graph,i*n_graph + 1)
            axes.clear()
            samples = dataSet.getsubsetbyLabel(hotword)
            files = [s.file for s in samples]
            data = files_to_feat(files, feature_param, autoTrim=True, zeroPadding=True)
            axes.imshow(np.mean(data, axis=0).T, interpolation='nearest', origin='lower')
            axes.set_title("{} (mean)".format(hotword))
            
            if display_variance:
                axes = self.figure.add_subplot(len(hotwords),n_graph,i*n_graph + 2)
                axes.clear()
                
                axes.imshow(np.var(data, axis=0).T, interpolation='nearest', origin='lower')
                axes.set_title("{} (variance)".format(hotword))
        
        self.canvas.draw()