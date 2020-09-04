
import os
import json
from random import shuffle

class DataSet:
    def __init__(self, dataSetName: str = "", labels: list = []):
        self.dataSetName = dataSetName
        self.labels = labels
        self.samples = []
        self.datasetFile = ""
        self.prep = False

    def saveDataSet(self, datasetPath: str ):
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
            self.samples.append(Sample({"label": label, "originalFile": f}))
        self._




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
        info += "Number of sample: {}".format(n_sample)

        for label in self.labels + [None]:
            info += sep
            n_sl = self.getsubsetbyLabel(label if label is not None else "non-hotword")
            info += "Sample of {}:\n".format(label)
            info += "\tSample count: {}, {}\n".format(n_sl, percent(n_sl, n_sample))
            
        return info

    ########################################################################
    ##### UTILS
    ########################################################################
    @classmethod
    def listFolder(cls, folderPath: str, recursive: bool = False, ext: str = '.wav') -> list:
        files = [os.path.join(folderPath,f) for f in os.listdir(folderPath) if f.endswith(ext)]
        if recursive:
            for d in [os.path.join(folderPath, d) for d in os.listdir(folderPath) if os.path.isdir(os.path.join(folderPath, d))]:
                files += DataSet.listFolder(os.path.join(folderPath, d), recursive=recursive, ext=ext)
        return files
    
class Sample:
    def __init__(self, sampleDict: dict = None):
        self.originalFile = "" # original File URI
        self.label = "" #sample label
        self.attr = "" # sample attribute
        self.procFile = "" # processed file URI
        self.featureFile = " " # feature file URI
        if sampleDict is not None:
            for key in sampleDict.keys() :
                if key in self.__dict__.keys():
                    self.__setattr__(key, sampleDict[key])

    @property
    def sampleDesc(self) -> dict:
        return {
            "label" : self.label,
            "originalFile" : self.originalFile,
            "attr" : self.attr,
            "procFile" : self.procFile,
            "featureFile" : self.featureFile,
        }

