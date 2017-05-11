# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\user\durgesh.n\workspace\Validations\source\Validations\ui\result_ui.ui'
#
# Created: Tue Feb 28 19:24:51 2017
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_errorNodesWin(object):
    def setupUi(self, errorNodesWin):
        errorNodesWin.setObjectName("errorNodesWin")
        errorNodesWin.resize(300, 400)
        errorNodesWin.setMinimumSize(QtCore.QSize(300, 400))
        errorNodesWin.setMaximumSize(QtCore.QSize(300, 400))
        self.centralwidget = QtGui.QWidget(errorNodesWin)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        errorNodesWin.setCentralWidget(self.centralwidget)

        self.retranslateUi(errorNodesWin)
        QtCore.QMetaObject.connectSlotsByName(errorNodesWin)

    def retranslateUi(self, errorNodesWin):
        errorNodesWin.setWindowTitle(QtGui.QApplication.translate("errorNodesWin", "ErrorNodesWin", None, QtGui.QApplication.UnicodeUTF8))

