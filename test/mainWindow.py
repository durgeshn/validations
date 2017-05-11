import os
import sys

from PySide import QtGui
from PySide import QtCore

import todo_ui


class ToDo(QtGui.QMainWindow, todo_ui.Ui_MainWindow):
    def __init__(self, prnt=None, config_path='T:/Vamshi/configs'):
        super(ToDo, self).__init__(prnt)
        self.setupUi(self)
        self.config_path = config_path
        self.treeWidget.setHeaderLabel('To Do List')
        self.treeWidget_2.setHeaderLabel('Done List')

        self.root_folder = os.path.dirname(__file__)

        self.fill_ui()
        self.connections()
        # ico = QtGui.QIcon()
        # self.toolButton.setIcon(ico)
        # self.toolButton.setText('')
        print self.root_folder, '<---------------------------------'

    def test(self, *args):
        itm = args[0]
        if itm.checkState(0) == QtCore.Qt.Checked:
            self.checkBox_checked_on(itm)
        elif itm.checkState(0) == QtCore.Qt.Unchecked:
            self.checkBox_checked_off(itm)

        self.update_config()

    def on_context_menu(self, point):
        """
        Right click pop-up menu.
        :param event:
        :type event:
        :return:
        :rtype:
        """
        menu = QtGui.QMenu(self)
        # new menu item
        new = QtGui.QAction('New', self)
        menu.addAction(new)
        # edit menu item
        edit = QtGui.QAction('Edit', self)
        menu.addAction(edit)
        menu.addSeparator()
        # settings menu item
        settings = QtGui.QAction('Settings', self)
        menu.addAction(settings)
        # make the connections.
        new.triggered.connect(self.make_new_config)
        edit.triggered.connect(self.edit_current_config)
        settings.triggered.connect(self.settings)
        # showing the menu.
        menu.exec_(self.toolButton.mapToGlobal(point))

    def make_new_config(self):
        print 'Make new Config files....'
        print self.config_path
        pass

    def edit_current_config(self):
        print 'Edit current Config file....'
        pass

    def settings(self):
        print 'Settings....'
        pass


    def checkBox_checked_on(self, itm):
        name = itm.text(0)
        self.treeWidget.blockSignals(True)
        self.treeWidget_2.blockSignals(True)

        self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(itm))
        child = QtGui.QTreeWidgetItem(self.treeWidget_2)
        child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)

        font = child.font(0)
        font.setStrikeOut(True)
        child.setFont(0, font)

        child.setText(0, "{}".format(name))
        child.setCheckState(0, QtCore.Qt.Checked)

        self.treeWidget.blockSignals(False)
        self.treeWidget_2.blockSignals(False)

    def checkBox_checked_off(self, itm):
        name = itm.text(0)
        self.treeWidget.blockSignals(True)
        self.treeWidget_2.blockSignals(True)

        self.treeWidget_2.takeTopLevelItem(self.treeWidget_2.indexOfTopLevelItem(itm))
        child = QtGui.QTreeWidgetItem(self.treeWidget)
        child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
        child.setText(0, "{}".format(name))
        child.setCheckState(0, QtCore.Qt.Unchecked)

        self.treeWidget.blockSignals(False)
        self.treeWidget_2.blockSignals(False)

    def connections(self):
        self.comboBox.currentIndexChanged.connect(self.combobox_itm_changed)
        self.treeWidget_2.itemChanged.connect(self.test)
        self.treeWidget.itemChanged.connect(self.test)

        self.toolButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.toolButton.customContextMenuRequested.connect(self.on_context_menu)

    def fill_ui(self):
        self.fill_combobox()

    def combobox_itm_changed(self):
        self.treeWidget.clear()
        self.treeWidget_2.clear()
        if self.comboBox.currentText() == 'SELECT':
            return
        data = self.read_config()

        self.treeWidget.blockSignals(True)
        self.treeWidget_2.blockSignals(True)

        for key, val in data.iteritems():
            if int(val):
                parent = self.treeWidget
                checkState = QtCore.Qt.Unchecked
            else:
                parent = self.treeWidget_2
                checkState = QtCore.Qt.Checked
            child = QtGui.QTreeWidgetItem(parent)

            if parent == self.treeWidget_2:
                font = child.font(0)
                font.setStrikeOut(True)
                child.setFont(0, font)

            child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
            child.setText(0, "{}".format(key))
            child.setCheckState(0, checkState)

        self.treeWidget.blockSignals(False)
        self.treeWidget_2.blockSignals(False)

    def fill_combobox(self):
        self.comboBox.clear()
        self.comboBox.addItem('SELECT')
        itm = list()
        for each in os.listdir(self.config_path):
            itm.append(each)
        self.comboBox.addItems(itm)

    def read_config(self):
        config_file_path = os.path.join(self.config_path, self.comboBox.currentText())
        print config_file_path
        data = dict()
        with open(config_file_path, 'r') as fid:
            for each in fid.readlines():
                tmp = each.strip().split(':')
                if len(tmp) == 0:
                    continue
                data[tmp[0]] = tmp[1]
        return data

    def update_config(self):
        # config_file_path = os.path.join(self.config_path, self.comboBox.currentText())
        # print config_file_path
        data = dict()
        for each in range(0, self.treeWidget.topLevelItemCount()):
            itm = self.treeWidget.topLevelItem(each)
            if itm.checkState(0) == QtCore.Qt.Unchecked:
                data[itm.text(0)] = False
            if itm.checkState(0) == QtCore.Qt.Checked:
                data[itm.text(0)] = True

        for each in range(0, self.treeWidget_2.topLevelItemCount()):
            itm = self.treeWidget_2.topLevelItem(each)
            if itm.checkState(0) == QtCore.Qt.Unchecked:
                data[str(itm.text(0))] = False
            if itm.checkState(0) == QtCore.Qt.Checked:
                data[str(itm.text(0))] = True
        # print data
        # import json
        # with open('D:/temp/aaa.txt', 'w') as fid:
        #     json.dump(data, fid, indent=4)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    cl = ToDo(config_path=r'D:\user\durgesh.n\workspace\Validations\source\Validations\test\config')
    cl.show()
    sys.exit(app.exec_())

