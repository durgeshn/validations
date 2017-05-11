import os
import sys

from PySide import QtGui
from PySide import QtCore

import playblastUI


class AAA(QtGui.QWidget, playblastUI.Ui_playblastUI):
    """
    This the the Class start.
    """
    def __init__(self, prnt=None):
        super(AAA, self).__init__(prnt)
        self.setupUi(self)
        self.resolution_LW.addItem('aaaaaaaaa')

def main():
    make_app = QtGui.QApplication(sys.argv)
    main_form = AAA()
    main_form.show()
    return make_app.exec_()

if __name__ == '__main__':
    main()
