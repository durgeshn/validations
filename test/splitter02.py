import sys
from PySide import QtGui, QtCore
from PySide.QtGui import QScrollArea

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        hbox = QtGui.QHBoxLayout(self)
        first = QtGui.QFrame(self)
        first.setFrameShape(QtGui.QFrame.StyledPanel)
        scrollAreaLeft = QScrollArea()
        scrollAreaLeft.setWidgetResizable(True)
        scrollAreaLeft.setWidget(first)
        second = QtGui.QFrame(self)
        second.setFrameShape(QtGui.QFrame.StyledPanel)
        scrollAreaRight = QScrollArea()
        scrollAreaRight.setWidgetResizable(True)
        scrollAreaRight.setWidget(second)
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(scrollAreaLeft)
        splitter.addWidget(scrollAreaRight)
        splitter.setSizes([10, 100])
        hbox.addWidget(splitter)
        self.setLayout(hbox)
        self.setGeometry(600, 600, 600, 600)
        self.setWindowTitle('QtGui.QSplitter')
        self.show()
        print ("scrollAreaLeft width: "+str(scrollAreaLeft.width()))
        print ("scrollAreaRight width: "+str(scrollAreaRight.width()))

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()