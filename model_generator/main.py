#!/usr/bin/env python3
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from interfaces.mainwindows import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()