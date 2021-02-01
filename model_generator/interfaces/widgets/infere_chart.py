from PyQt5 import QtChart, QtWidgets, QtGui

class InfereChart(QtWidgets.QWidget):
    def __init__(self, labels: list, threshold: float, width: float = 5.0):
        QtWidgets.QWidget.__init__(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.chart = QtChart.QChart()
        self.chartView = QtChart.QChartView(self.chart)
        self.chartView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.layout.addWidget(self.chartView)
        self.setLayout(self.layout)
        
        self.width = width
        self.threshold = threshold

        self.series = []
        for label in labels:
            serie = QtChart.QLineSeries()
            serie.setName(label)
            self.series.append(serie)
            self.chart.addSeries(serie)

        self.threshold_serie = QtChart.QLineSeries()
        self.threshold_serie.setName("threshold")
        self.threshold_serie.setPen(QtGui.QPen(QtGui.QColor("black")))


        self.threshold_serie.append(0, self.threshold)
        self.threshold_serie.append(width, self.threshold)
        self.chart.addSeries(self.threshold_serie)
        
        self.chart.createDefaultAxes()
        self.chart.axisX().setRange(0 , width)
        self.chart.axisY().setRange(0, 1)

        self.chartView.show()

    def addValue(self, xValue, yValue: list):
        """ Add a single step values """
        for i, serie in enumerate(self.series):
            self.series[i].append(xValue, yValue[i])
        self.updateView(xValue)

    def addValues(self, xValue: list, yValue: list):
        for i, x in xValues:
            for j, serie in enumerate(self.series):
                self.series[j].append(x, yValue[i][j])
        self.updateView(xValue[-1])

    def setThreshold(self, value):
        self.threshold = value
        self.threshold_serie.clear()
        self.threshold_serie.append(0, self.threshold)
        self.threshold_serie.append(3600, self.threshold)

    def updateView(self, xValue):
        self.chart.axisX().setRange(xValue - self.width , xValue)
        self.threshold_serie.clear()
        self.threshold_serie.append(xValue - self.width, self.threshold)
        self.threshold_serie.append(xValue, self.threshold)
        self.chartView.update()
        
    def clear(self):
        for serie in self.series:
            serie.clear()
