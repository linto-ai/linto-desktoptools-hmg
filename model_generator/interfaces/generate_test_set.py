import os
import sys
import json
from shutil import copyfile

from PyQt5 import QtCore, QtGui, QtWidgets

from interfaces.ui.generate_testset_ui import Ui_Dialog
from scripts.qtutils import create_infoline_layout, create_horizontal_line, create_vertical_spacer

if getattr(sys, 'frozen', False):
    DIR_PATH = os.path.dirname(sys.executable)
else:
    DIR_PATH = os.path.dirname(__file__)

class TestSetDialog(QtWidgets.QDialog):
    def __init__(self, parent, manifest):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.data_location = manifest['data']['samples_location']
        self.present_data()

        #connect
        self.ui.browse_PB.clicked.connect(self.on_browse_clicked)
        self.ui.create_PB.clicked.connect(self.on_create_clicked)
        self.ui.cancel_PB.clicked.connect(self.close)

    def present_data(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("TestSet Data"))
        for cl in self.data_location.keys():
            layout.addWidget(create_horizontal_line())
            layout.addLayout(create_infoline_layout(cl, "{} samples".format(str(self.data_location[cl]['test']['count']))))
        layout.addItem(create_vertical_spacer())
        self.ui.data_desc_GB.setLayout(layout)

    def on_browse_clicked(self):
        res = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a directory", "/home/")
        if res is not None:
            self.ui.location_LE.setText(res)
    
    def on_create_clicked(self):
        if self.ui.location_LE.text() == '':
            self.on_browse_clicked()
            if self.ui.location_LE.text() == '':
                return
        self.create_test_set()

    def create_test_set(self):
        testset_manifest = dict()
        testset_name = self.ui.testsetname_LE.text().replace(' ', '')
        testset_path = os.path.join(self.ui.location_LE.text(), testset_name)
        os.mkdir(testset_path)

        testset_manifest['name'] = testset_name
        testset_manifest['hotwords'] = [k for k in self.data_location.keys()]
        
        for cl in self.data_location.keys():
            cl_path = os.path.join(testset_path, cl)
            os.mkdir(cl_path)
            testset_manifest[cl] = dict()
            i = 0
            for d in self.data_location[cl]['test']['folders']:
                for f in [f for f in os.listdir(d) if f.endswith('.wav')]:
                    old_path = os.path.join(d, f)
                    new_path = os.path.join(cl_path, f)
                    copyfile(old_path, new_path)
                    i += 1
            testset_manifest[cl]['samples_count'] = i
        man_path = os.path.join(testset_path, testset_name + '.testset')
        with open(man_path, 'w') as f:
            json.dump(testset_manifest, f)
        self.close()
        