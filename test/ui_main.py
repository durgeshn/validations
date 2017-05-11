# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\vamshikrishna\Desktop\untitled.ui'
#
# Created: Tue Mar 21 14:23:11 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
from PySide.QtGui import QApplication,QMainWindow,QFileDialog,QMessageBox,QDialog
import sys
import os

class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        print "in init"
        self.setupUi(self)

    def setupUi(self, Window):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(614, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(49, 69, 531, 221))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        # self.checkBox = QtGui.QCheckBox(self.verticalLayoutWidget)
        # self.checkBox.setObjectName("checkBox")
        # self.verticalLayout.addWidget(self.checkBox)
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(50, 20, 231, 22))
        self.comboBox.setObjectName("comboBox")
        # self.comboBox.activated.connect(self.read_config)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(390, 20, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(50, 320, 531, 231))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        # self.checkBox_2 = QtGui.QCheckBox(self.verticalLayoutWidget_2)
        # self.checkBox_2.setObjectName("checkBox_2")
        # self.verticalLayout_2.addWidget(self.checkBox_2)
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(290, 20, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 614, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)



        # self.list_config()
        # self.create_checkboxes()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        # self.checkBox.setText(QtGui.QApplication.translate("MainWindow", "CheckBox", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        # self.checkBox_2.setText(QtGui.QApplication.translate("MainWindow", "CheckBox", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MainWindow", "Select", None, QtGui.QApplication.UnicodeUTF8))


    def list_config(self):
        config = os.listdir(r'T:\vamshi\configs')
        self.comboBox.addItems(config)
         # self.pushButton.clicked.connect(self,os.file.readlines(r'T:\vamshi\configs\*.txt'), 'r')

    # def read_config(self):
    #     print self.comboBox.currentText()
    #     d = []
    #     with open('T://vamshi//configs//' + self.comboBox.currentText(), 'r') as f:
    #         data = f.readlines()
    #         print data
    #         data.pop(-1)
    #         print data
    #         for i in data:
    #             # print i
    #             d =  i.rstrip('\n').split(':')
    #             print d[1]


    # def create_checkboxes(self):
    #     with open('T://vamshi//configs//' + self.comboBox.currentText(), 'r') as fid:
    #         checklist = [fid.readlines()]
    #         if checklist[1] == 0:
    #             self.checkBox_3.setText







            # for line in f:
            #     print "$$$$$$$", line
            #     (key, val) = line.split(':')
            #     print key,val
            #     d[str(key)] = str(val)
            # print d


        # filedata = {}
        # with open("D:\\python\\chklistdata\\"+filename, "r") as f:
        #     for line in f:
        #         # print line
        #         (key, val) = line.rstrip('\n').split(":")
        #         filedata[key] = val
        # print filedata
    # def create_checkboxes(self):
    #     self.read_config()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    cl = Ui_MainWindow()
    cl.show()
    sys.exit(app.exec_())
