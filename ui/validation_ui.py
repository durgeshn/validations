# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\user\durgesh.n\workspace\Validations\source\Validations\ui\validation_ui.ui'
#
# Created: Wed Mar 01 15:35:50 2017
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(359, 385)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.proj_cb = QtGui.QComboBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.proj_cb.sizePolicy().hasHeightForWidth())
        self.proj_cb.setSizePolicy(sizePolicy)
        self.proj_cb.setObjectName("proj_cb")
        self.gridLayout.addWidget(self.proj_cb, 0, 0, 1, 1)
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.treeWidget.headerItem().setText(1, "2")
        self.treeWidget.headerItem().setText(2, "3")
        self.treeWidget.headerItem().setText(3, "4")
        self.treeWidget.header().setDefaultSectionSize(200)
        self.gridLayout.addWidget(self.treeWidget, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.select_all_tb = QtGui.QToolButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.select_all_tb.sizePolicy().hasHeightForWidth())
        self.select_all_tb.setSizePolicy(sizePolicy)
        self.select_all_tb.setMinimumSize(QtCore.QSize(70, 20))
        self.select_all_tb.setObjectName("select_all_tb")
        self.horizontalLayout.addWidget(self.select_all_tb)
        self.run_tb = QtGui.QToolButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_tb.sizePolicy().hasHeightForWidth())
        self.run_tb.setSizePolicy(sizePolicy)
        self.run_tb.setMinimumSize(QtCore.QSize(70, 20))
        self.run_tb.setObjectName("run_tb")
        self.horizontalLayout.addWidget(self.run_tb)
        self.run_all_tb = QtGui.QToolButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_all_tb.sizePolicy().hasHeightForWidth())
        self.run_all_tb.setSizePolicy(sizePolicy)
        self.run_all_tb.setMinimumSize(QtCore.QSize(70, 20))
        self.run_all_tb.setObjectName("run_all_tb")
        self.horizontalLayout.addWidget(self.run_all_tb)
        self.refresh_tb = QtGui.QToolButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.refresh_tb.sizePolicy().hasHeightForWidth())
        self.refresh_tb.setSizePolicy(sizePolicy)
        self.refresh_tb.setMinimumSize(QtCore.QSize(70, 20))
        self.refresh_tb.setObjectName("refresh_tb")
        self.horizontalLayout.addWidget(self.refresh_tb)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.select_all_tb.setText(QtGui.QApplication.translate("MainWindow", "select All", None, QtGui.QApplication.UnicodeUTF8))
        self.run_tb.setText(QtGui.QApplication.translate("MainWindow", "Run", None, QtGui.QApplication.UnicodeUTF8))
        self.run_all_tb.setText(QtGui.QApplication.translate("MainWindow", "Run All", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_tb.setText(QtGui.QApplication.translate("MainWindow", "Refresh", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == '__main__':
    import sys
    make_app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    main_form = Ui_MainWindow(QtGui.QMainWindow)  # We set the form to be our ExampleApp (design)
    main_form.setupUi(main_form)
    # main_form.show()  # Show the form
    # return main_form
    # return make_app.exec_()  # and execute the app