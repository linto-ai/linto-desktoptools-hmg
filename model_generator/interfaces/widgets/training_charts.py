from PyQt5 import QtChart, QtWidgets, QtGui

class TrainingChart(QtWidgets.QWidget):
    def __init__(self, serieNames: list, bottomToTop: bool = True):
        QtWidgets.QWidget.__init__(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.chart = QtChart.QChart()
        self.chartView = QtChart.QChartView(self.chart)
        self.chartView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.layout.addWidget(self.chartView)
        self.setLayout(self.layout)
        
        self.bottomToTop = bottomToTop # Used to update the Y axis range

        self.series = []
        self.names = serieNames
        for name in serieNames:
            serie = QtChart.QLineSeries()
            serie.setName(name)
            self.series.append(serie)
            self.chart.addSeries(serie)
        
        self.chart.createDefaultAxes()
        self.chart.axisX().setRange(0,100)
        self.chart.axisY().setRange(0,1)

        self.chartView.show()

    def load(self, seriesValues: tuple):
        self.clear()
        for i, serie in enumerate(seriesValues):
            for x, y in zip(serie[0], serie[1]):
                self.series[i].append(x, y)
                self.series[i].setName(self.names[i] + " {:.5}".format(y))
        self.updateRange()
        self.chartView.update()
        self.setRangeX(min(seriesValues[0][0]), max(seriesValues[0][0]))

    def append(self, values: tuple):
        for i, point in enumerate(values):
            self.series[i].append(point[0], point[1])
            self.series[i].setName(self.names[i] + " {:.5}".format(point[1]))
        self.updateRange()
        self.chartView.update()

    def getSeriesMinY(self) -> float:
        minest = 1.0 # don't judge me, min and max are reserved keywords
        for serie in self.series:
            minest = min([minest, min([point.y() for point in serie.pointsVector()])])
        return minest
    
    def getSeriesMaxY(self) -> float:
        maxest = 0.0
        for serie in self.series:
            maxest = max([maxest, max([point.y() for point in serie.pointsVector()])])
        return maxest

    def setRangeX(self, min_v, max_v):
        self.chart.axisX().setRange(min_v, max_v)

    def updateRange(self):
        if self.bottomToTop:
            self.chart.axisY().setRange(self.getSeriesMinY(), 1)
        else:
            self.chart.axisY().setRange(0, self.getSeriesMaxY())

    def clear(self):
        for i, serie in enumerate(self.series):
            serie.clear()
            serie.setName(self.names[i])

    def getValues(self) -> list:
        """ Return a list([epoch], [serie_1], ..., [serie_n]) """ 
        values = list()
        values.append([point.x() for point in self.series[0].pointsVector()]) # Epochs
        for serie in self.series:
            values.append([point.y() for point in serie.pointsVector()])
        return values