
import os
import json
from random import shuffle
import shutil

from PyQt5 import QtCore

class Sample:
    def __init__(self, sampleDict: dict = None):
        self.file = "" # File URI
        self.label = "" # Sample label
        self.attr = "" # Sample attribute
        self.proc = None # Processing description (None if original)
        self.originalFile = None # Original file name (None if original)
        self.featureFile = None
        if sampleDict is not None:
            for key in sampleDict.keys():
                if key in self.__dict__.keys():
                    self.__setattr__(key, sampleDict[key])

    @property
    def sampleDesc(self) -> dict:
        return {
            "label" : self.label,
            "file" : self.file,
            "attr" : self.attr,
            "proc" : self.proc,
            "originalFile" : self.originalFile,
            "featureFile" : self.featureFile
        }
    
    def __eq__(self, other):
        return self.file == other.file

class DataSet(QtCore.QObject):
    """ DataSet represent a collection of audio samples.
    The class provides methods to manage, select and export data.
    """

    dataset_updated = QtCore.pyqtSignal(name='dataset_updated')
    progress_notification = QtCore.pyqtSignal(int, int, name='progress_notification') # show progress on long processing

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
    
    def addSample(self, sample: Sample):
        self.samples.append(sample)

    def removeSamples(self, samples: list):
        for sample in self.samples:
            if sample in samples:
                self.samples.remove(sample)
        self.saveDataSet()
        self.dataset_updated.emit()
    
    def addFromManifest(self, manifestRoot, manifest):
        for s in manifest:
            self.samples.append(Sample({"label": s["label"], "file" : os.path.join(manifestRoot, s["file"])}))
        self.saveDataSet()
        self.dataset_updated.emit()


    ########################################################################
    ##### SET MANIPULATION
    ########################################################################

    def getsubsetbyLabel(self, label) -> list:
        label = label if label is not None else ""
        return [s for s in self.samples if s.label == label]

    def formSets(self, distribution: tuple) -> tuple:
        '''  Divide the dataset into 3 sets (train, val, test) according to the [distribution] values'''
        train_set = DataSet("train", self.labels)
        val_set = DataSet("val", self.labels)
        test_set = DataSet("test", self.labels)
    
        # Split the data by labels
        shuffle(self.samples)
        for label in self.labels + [None]:
            subset = self.getsubsetbyLabel(label)
            delimiter_1 = int(distribution[0] * len(subset))
            delimiter_2 = delimiter_1 + int(distribution[1] * len(subset))
            train_set.samples.extend(subset[:delimiter_1])
            val_set.samples.extend(subset[delimiter_1:delimiter_2])
            test_set.samples.extend(subset[delimiter_2:])

        return (train_set, val_set, test_set)

    def __iadd__(self, other):
        self.samples.extend(other.samples)
        return self
        
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
    def exportDataSet(self, exportName : str, exportPath : str, trace : bool = False):
        """ Export this dataset to selected folder with data selected.
        """
        targetFolder = os.path.join(exportPath, exportName)
        if not os.path.isdir(targetFolder):
            os.mkdir(targetFolder)
        manifest = []
        n_sample = len(self.samples)
        counter = 0
        for s in self.samples:
            baseName = os.path.basename(s.file)
            shutil.copy(s.file, os.path.join(targetFolder, baseName))
            sample_desc = dict()
            sample_desc['file'] = baseName
            sample_desc['label'] = s.label
            manifest.append(sample_desc)
            counter += 1
            if trace:
                self.progress_notification.emit(counter, n_sample)

        with open(os.path.join(targetFolder, "{}.json".format(exportName)), 'w') as f:
            json.dump(manifest, f)

        #TODO handle copy errors       

    def importDataSet(self, manifestPath):
        with open(manifestPath, 'r') as f:
            manifest = json.load(f)
        self.addFromManifest(os.path.dirname(manifestPath), manifest)


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

    

