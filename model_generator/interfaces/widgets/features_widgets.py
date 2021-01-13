from PyQt5 import QtWidgets, QtCore

from .ui.mfcc_ui import Ui_MFCC

class MFCC(QtWidgets.QWidget):
    features_changed = QtCore.pyqtSignal(name='features_changed')
    def __init__(self, default: dict):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_MFCC()
        self.ui.setupUi(self)
        
        self.load_values(default)
        
        self.ui.nfft_SP.valueChanged.connect(lambda: self.features_changed.emit())
        self.ui.nfilt_SP.valueChanged.connect(self.onNumFiltChanged)
        self.ui.ncoef_SP.valueChanged.connect(self.onNumCoefChanged)
        self.ui.use_energy_CB.stateChanged.connect(lambda: self.features_changed.emit())

    def load_values(self, values: dict):
        self.ui.nfft_SP.setValue(values.get("fft_size", 512))
        self.ui.nfilt_SP.setValue(values.get("n_filters", 20))
        self.ui.ncoef_SP.setValue(values.get("n_coefs", 13))
        self.ui.use_energy_CB.setChecked(values.get("use_logenergy", False))

    def onNumCoefChanged(self, value):
        if value >= self.ui.nfilt_SP.value():
            self.ui.nfilt_SP.setValue(value + 1)
        self.features_changed.emit()
    
    def onNumFiltChanged(self, value):
        if value <= self.ui.ncoef_SP.value():
            self.ui.ncoef_SP.setValue(value - 1)
        self.features_changed.emit()

    def getValues(self) -> dict:
        values = dict()
        values["fft_size"] = self.ui.nfft_SP.value()
        values["n_filters"] = self.ui.nfilt_SP.value()
        values["n_coefs"] = self.ui.ncoef_SP.value()
        values["use_logenergy"] = self.ui.use_energy_CB.isChecked()
        return values
