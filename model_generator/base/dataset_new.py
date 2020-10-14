
import os
import json
from random import shuffle
import shutil

from PyQt5 import QtCore

class DataSet(QtCore.QObject):
    """ DataSet represent a collection of audio samples.
    The class provides methods to manage, select and export data.
    """

    dataset_updated = QtCore.pyqtSignal(name='dataset_updated')

    def __init__(self, dataSetName: str = "", labels: list = []):
        QtCore.QObject.__init__(self)
        self.dataSetName = dataSetName
        self.labels = labels
        self.samples = []
        self.datasetFile = ""
        self.prep = False

    def saveDataSet(self, datasetPath: str = None):
        datasetPath = datasetPath if datasetPath is not None else self.datasetFile
        datasetContent = dict()
        datasetContent["name"] = self.dataSetName
        datasetContent["labels"] = self.labels
        datasetContent["samples"] = [s.sampleDesc for s in self.samples]
        with open(datasetPath, 'w') as f:
            json.dump(datasetContent, f)

    def loadDataSet(self, datasetPath: str):
        self.datasetFile = datasetPath
        with open(datasetPath, 'r') as f:
            datasetContent = json.load(f)
        self.dataSetName = datasetContent["name"]
        self.labels = datasetContent["labels"]
        self.samples = [Sample(s) for s in datasetContent["samples"]]

    ########################################################################
    ##### DATA MANAGEMENT
    ########################################################################

    def addSampleFiles(self, label, files):
        for f in files:
            self.samples.append(Sample({"label": label, "file": f}))
        self.saveDataSet()
        self.dataset_updated.emit()

    def addFileFromManifest(self, manifestPath):
        #TODO
        pass

    ########################################################################
    ##### SET MANIPULATION
    ########################################################################

    def getsubsetbyLabel(self, label) -> list:
        return [s for s in self.samples if s.label == label]

    
    ########################################################################
    ##### DISPLAY
    ########################################################################

    def datasetInfo(self) -> str:
        sep = "\n" + "-"*15 +"\n"
        percent = lambda n, d : "{:.2f}%".format(n/d*100)
        info = "Dataset Name : {}\n".format(self.dataSetName)
        info += "Labels: {}\n".format(str(self.labels))
        n_sample = len(self.samples)
        if n_sample == 0:
            info += "No sample yet.\n"
            return info
        info += "Number of samples: {}".format(n_sample)

        for label in self.labels + [None]:
            info += sep
            n_sl = len(self.getsubsetbyLabel(label if label is not None else ""))
            info += "Samples of {}:\n".format(label if label is not None else "non-hotword")
            info += "\tSample count: {} ({})\n".format(n_sl, percent(n_sl, n_sample))
            
        return info

    def datasetValues(self) -> list:
        """ Return dataset data values as a list of tuples of (label, number of samples, percentage on dataset) """
        values = []
        percent = lambda n, d : "{:.2f}%".format(n/(d if d > 0 else 1)*100)
        n_sample = len(self.samples)
        for label in self.labels + [None]:
            n_sl = len(self.getsubsetbyLabel(label if label is not None else ""))
            label = label if label is not None else "non-hotword"
            values.append((label, n_sl, percent(n_sl, n_sample)))
        return values

    ########################################################################
    ##### IMPORT / EXPORT
    ########################################################################
    def exportDataSet(self, exportPath : str, exportedName: str, rawData : bool = True, procData : bool = True, compress : bool = False):
        """ Export this dataset to selected folder with data selected.
        
        Keyword arguments:
        rawData -- export unprocessed data (default True)
        procData -- export processed data (default True)
        compress -- put the exported dataset in a compressed archive (default False)
        """
        pass

    def importDataSet(self, manifestPath):
        pass

    ########################################################################
    ##### UTILS
    ########################################################################
    @classmethod
    def listFolder(cls, folderPath: str, recursive: bool = False, ext: str = '.wav') -> list:
        """ List folder content and return a list of absolute path. 
        
        Keyword arguments:
        recursive -- Recursive search (default False)
        ext -- File extension filer (default .wav)
        """
        files = [os.path.join(folderPath,f) for f in os.listdir(folderPath) if f.endswith(ext)]
        if recursive:
            for d in [os.path.join(folderPath, d) for d in os.listdir(folderPath) if os.path.isdir(os.path.join(folderPath, d))]:
                files += DataSet.listFolder(os.path.join(folderPath, d), recursive=recursive, ext=ext)
        return files
    
class Sample:
    def __init__(self, sampleDict: dict = None):
        self.fileURI = "" # File URI
        self.label = "" # Sample label
        self.attr = "" # Sample attribute
        self.proc = None # Processing description (None if original)
        self.originalFile = None # Original file name (None if original)
        if sampleDict is not None:
            for key in sampleDict.keys():
                if key in self.__dict__.keys():
                    self.__setattr__(key, sampleDict[key])

    @property
    def sampleDesc(self) -> dict:
        return {
            "label" : self.label,
            "file" : self.fileURI,
            "attr" : self.attr,
            "proc" : self.proc,
            "originalFile" : self.originalFile,
        }

