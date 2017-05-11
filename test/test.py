import sys
import json

from PySide import QtGui
from PySide import QtCore

import extra_ui


class EditConfig(QtGui.QMainWindow, extra_ui.Ui_MainWindow):
    def __init__(self, prnt=None, config_file=''):
        super(EditConfig, self).__init__(prnt)
        self.setupUi(self)
        self.config = config_file

        self.data = None
        self.undoStack = QtGui.QUndoStack(self)
        self.initUI()

    def initUI(self):
        self.update_ui()
        self.makeConnections()
        self.make_undo_hotkey()
        self.make_delete_hotkey()
        self.make_redo_hotkey()

    def makeConnections(self):
        self.pushButton_3.clicked.connect(self.deleteButtonCMD)
        self.pushButton_2.clicked.connect(self.cancelButtonCMD)
        self.pushButton.clicked.connect(self.doneButtonCMD)

    def deleteButtonCMD(self):
        print 'deleteButtonCMD'
        rowSelected = self.listWidget.currentRow()
        item = self.listWidget.item(rowSelected)
        if item is None:
            return
        command = CommandDelete(self.listWidget, item, rowSelected, "Delete item '{0}'".format(item.text()))
        self.undoStack.push(command)

    def make_undo_hotkey(self):
        undo_menu = QtGui.QAction(QtGui.QIcon(), 'undo', self)
        undo_menu.setShortcut('Ctrl+z')
        undo_menu.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.addAction(undo_menu)
        undo_menu.triggered.connect(self.undoStack.undo)

    def make_redo_hotkey(self):
        redo_menu = QtGui.QAction(QtGui.QIcon(), 'redo', self)
        redo_menu.setShortcut('Ctrl+Shift+z')
        redo_menu.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.addAction(redo_menu)
        redo_menu.triggered.connect(self.undoStack.redo)

    def make_delete_hotkey(self):
        delete_menu = QtGui.QAction(QtGui.QIcon(), 'delete', self)
        delete_menu.setShortcut('Delete')
        delete_menu.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.addAction(delete_menu)
        delete_menu.triggered.connect(self.deleteButtonCMD)

    def doneButtonCMD(self):
        self.undoStack.undo()
        print 'doneButtonCMD'

    def cancelButtonCMD(self):
        print 'cancelButtonCMD'
        self.close()

    def read_config(self):
        self.data = None
        with open(self.config, 'r') as fid:
            self.data = json.load(fid)

    def update_ui(self):
        self.listWidget.clear()
        self.read_config()
        print self.data
        for k, v in self.data.iteritems():
            print k, v
            itm = QtGui.QListWidgetItem(k, parent=self.listWidget)
            itm.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.listWidget.addItem(itm)


class CommandDelete(QtGui.QUndoCommand):
    def __init__(self, listWidget, item, row, description):
        super(CommandDelete, self).__init__(description)
        self.listWidget = listWidget
        self.string = item.text()
        self.row = row

    def redo(self):
        self.listWidget.takeItem(self.row)

    def undo(self):
        addItem = QtGui.QListWidgetItem(self.string)
        # addItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        addItem.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.listWidget.insertItem(self.row, addItem)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    cl = EditConfig(config_file=r'D:\user\durgesh.n\workspace\Validations\source\Validations\test\config\aaa.txt')
    cl.show()
    sys.exit(app.exec_())
