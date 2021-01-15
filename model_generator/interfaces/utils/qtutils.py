from PyQt5 import QtGui, QtWidgets, QtCore

def create_infoline_layout(name, value):
    font = QtGui.QFont()
    font.setPointSize(12)
    font.setBold(True)
    font.setUnderline(True)
    layout = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(name)
    label.setFont(font)
    layout.addWidget(label)
    layout.addWidget(QtWidgets.QLabel(value))
    layout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    return layout
        
def create_horizontal_line():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    return line

def create_vertical_line():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.VLine)
    return line

def create_vertical_spacer():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

def create_horizontal_spacer():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

def empty_layout(layout):
    if layout is not None:
        for i in reversed(range(layout.count())): 
            widgetToRemove = layout.itemAt(i).widget()
            layout.removeWidget(widgetToRemove)
            if not widgetToRemove is None:
                widgetToRemove.setParent(None)

def empty_list_widget(listwidget, condition: callable = lambda x : True):
    """ Empty a QListWidget according to a condition

    Keyword arguments:
    ==================
    listwidget (QtWidget.QListWidget) -- The list to empty

    condition (callable) -- A function to determine if the element must be deleted. The function is applied on the internal widget (default is True for all)

    Condition Exemple: condition=lambda x: x.checkbox.isChecked() -> the element is deleted if its internal checkbox is checked.

    """
    delete_list = []
    for i in range(listwidget.count()):
        item = listwidget.item(i)
        widget = listwidget.itemWidget(item)
        if widget.CB.isChecked():
            delete_list.append(i)
    delete_list.reverse()
    for i in delete_list:
        listwidget.takeItem(i)

class CustomButton(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(QtWidgets.QWidget, name='clicked')
    
    def __init__(self, instance: QtWidgets.QWidget, title: str, infoText: str, iconPath: str = None):
        self.instance = instance
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setSpacing(15)
        QtWidgets.QFrame.__init__(self)
        self.title = QtWidgets.QLabel(title)
        self.title.setStyleSheet("font-weight: bold;")
        self.title.setWordWrap(True)
        if iconPath is not None:
            icon = QtWidgets.QLabel()
            iconMap = QtGui.QPixmap(iconPath)
            icon.setPixmap(iconMap)
            icon.setFixedSize(50,50)
            icon.setScaledContents(True)
            self.titleLayout.addWidget(icon)
        self.titleLayout.addWidget(self.title)
        self.description = QtWidgets.QLabel(infoText)
        self.description.setWordWrap(True)

        self.mainLayout.addLayout(self.titleLayout)
        self.mainLayout.addWidget(self.description)
        self.setLayout(self.mainLayout)

        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
        self.setMaximumSize(300,200)
        self.setMinimumSize(300,100)

    def mouseReleaseEvent(self, event):
        if self.isEnabled:
            self.clicked.emit(self.instance)
        