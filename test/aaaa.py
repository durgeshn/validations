import homescreen4

import sys
from PySide import QtGui, QtCore


class AA(QtGui.QWidget, homescreen4.Ui_Form):
    def __init__(self, prnt=None):
        super(AA, self).__init__(prnt)
        self.setupUi(self)

if __name__ == '__main__':
    qapp = QtGui.QApplication(sys.argv)
    a = AA()
    a.show()
    qapp.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
    qapp.exec_()
