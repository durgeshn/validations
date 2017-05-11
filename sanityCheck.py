"""
This is the main ui module for the SanityCheck.
"""
# general imports.
import os
import inspect
import ConfigParser

# Qt imports.
from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

# custom imports.
from Validations.core.rig import RigValidations
from Validations.core.anim import animValidations
from Validations.ui import validation_ui
from Validations.ui import result_ui

# maya imports.
import pymel.core as pm
import maya.OpenMayaUI as omui
# from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# reload custom imports.
reload(animValidations)
reload(RigValidations)
reload(validation_ui)


def maya_main_window():
    """
    This is to get the maya window QT pointer.
    :return:
    :rtype:
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

sshFile=r"D:\user\durgesh.n\workspace\Validations\source\Validations\ui\QTDark.stylesheet"
QTDark = None
with open(sshFile,"r") as fh:
    QTDark = fh.read()


# class Validator(MayaQWidgetDockableMixin, QtGui.QMainWindow, validation_ui.Ui_MainWindow):
class Validator(QtGui.QMainWindow, validation_ui.Ui_MainWindow):
    """
    This the the Class start.
    """
    def __init__(self, debug=False, tool_for='rig'):
        super(Validator, self).__init__()
        self.setObjectName('sanity_check_window')
        self.debug = debug
        self.tool_for = tool_for
        self.root_folder = os.path.dirname(__file__)
        self.setupUi(self)
        self.setWindowTitle('PCGI Validation Checks : %s' % self.tool_for)
        self.setMinimumWidth(385)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setColumnCount(5)
        self.treeWidget.setColumnWidth(0, 200)
        self.treeWidget.setColumnWidth(1, 50)
        self.treeWidget.setColumnWidth(2, 35)
        self.treeWidget.setColumnWidth(3, 35)
        self.treeWidget.setColumnWidth(3, 35)
        self.treeWidget.setColumnWidth(4, 35)
        self.treeWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        self.fill_ui()
        self.select_all_tb.setText('Toggle Selection All')
        self.populateProjects()
        self.connections()

        self.setStyleSheet(QTDark)

    def populateProjects(self):
        """
        Populate projects from the config location.
        :return:
        :rtype:
        """
        self.proj_cb.clear()
        config_folder = os.path.join(os.path.dirname(__file__), 'config').replace('\\', '/')
        projects = [x for x in os.listdir(config_folder) if not x == 'default']
        self.proj_cb.addItems(projects)
        self.proj_cb.insertItem(0, 'default')
        self.proj_cb.setCurrentIndex(0)

    def get_config_file(self, proj):
        """
        Get the config file for the project else return default.
        :return:
        :rtype:
        """
        config_folder = os.path.join(os.path.dirname(__file__), 'config').replace('\\', '/')
        # print config_folder
        if not proj:
            proj = 'default'
        else:
            proj = proj.lower()
        config_file = os.path.join(config_folder, proj)
        # print config_file
        return config_file

    def get_parser(self, proj):
        """
        Make the parser with the config file.
        :return:
        :rtype:
        """
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(self.get_config_file(proj))
        return config_parser

    def connections(self):
        """
        Do all connections here.
        :return:
        :rtype: None
        """
        self.select_all_tb.clicked.connect(self.toggle_all_def)
        self.run_tb.clicked.connect(self.run_def)
        self.run_all_tb.clicked.connect(self.run_all)
        self.refresh_tb.clicked.connect(self.refereshDef)
        self.proj_cb.currentIndexChanged.connect(self.fill_ui)

    def getValidations(self, proj):
        parser = self.get_parser(proj)
        return parser.get('VALIDATIONS', self.tool_for)

    def refereshDef(self):
        """
        Refreshes the UI.
        :return:
        :rtype:
        """
        self.treeWidget.clear()
        self.fill_ui()

    def fill_ui(self):
        """
        Fill up the UI.
        :return:
        :rtype: None
        """
        projectName = self.proj_cb.currentText()
        validValidations = self.getValidations(projectName)
        self.treeWidget.clear()

        valid_dept = list()
        if self.tool_for == 'rig':
            valid_dept = inspect.getmembers(RigValidations, inspect.isclass)

        if self.tool_for == 'anim':
            valid_dept = inspect.getmembers(animValidations, inspect.isclass)

        for each in valid_dept:
            # print each, '<------------------------------------------'
            # self.addItemToTree(each[0])
            if each[0] in ['MayaValidations', 'TestingTheUI']:
                if not self.debug:
                    continue
            # print validValidations, '<========================================'
            if not each[0] in validValidations:
                continue

            class_i = None
            if self.tool_for == 'rig':
                class_i = 'RigValidations.%s("%s")' % (each[0], projectName)
            if self.tool_for == 'anim':
                class_i = 'animValidations.%s("%s")' % (each[0], projectName)

            class_init = eval(class_i)
            class_init.project = projectName
            item = CustomTreeItem(self.treeWidget, each[0], class_init, self.root_folder)
            item.setData(66, QtCore.Qt.UserRole, class_init)

    def toggle_all_def(self):
        """
        This is the toggle the switch ON/OFF on all.
        :return:
        :rtype:
        """
        # i = 0
        for each in range(self.treeWidget.topLevelItemCount()):
            itm = self.treeWidget.topLevelItem(each)
            cb = self.treeWidget.itemWidget(itm, 1)
            i = 1 - cb.currentIndex()
            cb.setCurrentIndex(i)

    def run_def(self, itm=''):
        """
        Run the validation and store the class related info here.
        :param itm:
        :type itm:
        :return:
        :rtype:
        """
        if not itm:
            itm = self.treeWidget.selectedItems()[0]
        cb = self.treeWidget.itemWidget(itm, 1)
        if str(cb.currentText()) == 'OFF':
            print 'Validation switched off SKIPPING...'
            return

        class_init = itm.data(66, QtCore.Qt.UserRole)
        class_init.run()

        error_icon = QtGui.QIcon(os.path.join(self.root_folder, 'ui/icons/NOTOK.png'))
        ok_icon = QtGui.QIcon(os.path.join(self.root_folder, 'ui/icons/OK.png'))
        warning_icon = QtGui.QIcon(os.path.join(self.root_folder, 'ui/icons/warning3.png'))
        tb = self.treeWidget.itemWidget(itm, 2)
        nodes_tb = self.treeWidget.itemWidget(itm, 3)
        fix_tb = self.treeWidget.itemWidget(itm, 4)
        if str(class_init.status) == 'OK':
            tb.setIcon(ok_icon)
        elif str(class_init.status) == 'WARNING':
            tb.setIcon(warning_icon)
        else:
            tb.setIcon(error_icon)

        nodes_tb.setEnabled(class_init.isNodes)
        fix_tb.setEnabled(class_init.isFixable)

    def run_all(self):
        """
        This is to run on all.
        :return:
        :rtype:
        """
        for each in range(self.treeWidget.topLevelItemCount()):
            self.run_def(self.treeWidget.topLevelItem(each))

    def contextMenuEvent(self, event):
        """
        Right click pop-up menu.
        :param event:
        :type event:
        :return:
        :rtype:
        """
        menu = QtGui.QMenu(self)
        menu.addAction('Run')
        menu.addAction('Toggle')
        menu.exec_(event.globalPos())


class CustomTreeItem(QtGui.QTreeWidgetItem):
    """
    Custom TreeWidgetItem since PySide don't work well with extra widgets attached to the TreeWidgetItems.
    """
    def __init__(self, parent, name, className, root_folder):
        super(CustomTreeItem, self).__init__(parent)
        # Column 0 - Text:
        self.root_folder = root_folder
        self.setText(0, name)
        self.className = className
        # self.parent = parent
        # Column 1 - Combobox:
        self.combobox = QtGui.QComboBox()
        self.combobox.addItems(['ON', 'OFF'])
        self.treeWidget().setItemWidget(self, 1, self.combobox)
        # Column 2 - Button:
        self.ok_pb = QtGui.QToolButton()
        ok_icon = QtGui.QIcon(os.path.join(self.root_folder, 'ui/icons/.png'))
        self.ok_pb.setMaximumHeight(25)
        self.ok_pb.setMaximumWidth(25)
        self.ok_pb.setIcon(ok_icon)
        self.treeWidget().setItemWidget(self, 2, self.ok_pb)
        # Column 3 - Button:
        self.log_pb = QtGui.QToolButton()
        log_icon = QtGui.QIcon(os.path.join(self.root_folder, 'ui/icons/logFile.png'))
        self.log_pb.setMaximumHeight(25)
        self.log_pb.setMaximumWidth(25)
        self.log_pb.setIcon(log_icon)
        # self.button.setText("button %s" % name)
        self.treeWidget().setItemWidget(self, 3, self.log_pb)
        # Column 4 - Button:
        self.fix_pb = QtGui.QToolButton()
        fix_icon = QtGui.QIcon(os.path.join(self.root_folder, 'ui/icons/wrench.png'))
        self.fix_pb.setMaximumHeight(25)
        self.fix_pb.setMaximumWidth(25)
        self.fix_pb.setIcon(fix_icon)
        self.treeWidget().setItemWidget(self, 4, self.fix_pb)

        # Signals
        self.treeWidget().connect(self.log_pb, QtCore.SIGNAL("clicked()"), self.log_def)
        self.treeWidget().connect(self.fix_pb, QtCore.SIGNAL("clicked()"), self.fix_def)

    def log_def(self):
        """
        Show the log window.
        :return:
        :rtype:
        """
        # msg = self.className.errorMessage
        # msg += '\n'.join([str(x) for x in self.className.errorNodes])

        log_win = LogWin(maya_main_window())
        # log_win.setWindowModality(QtCore.Qt.WindowModal)
        log_win.listWidget.addItems([str(x) for x in self.className.errorNodes])
        log_window = log_win.show()
        # self.exec_()
        return log_window

    def fix_def(self):
        """
        Run the fixes if there is any.
        :return:
        :rtype:
        """
        # print self.className.errorMode, '<-------------------------------------'
        # if self.className.errorMode == 'ERROR' or self.className.errorMode == 'WARNING':
        self.className.fix()


class LogWin(QtGui.QMainWindow, result_ui.Ui_errorNodesWin):
    """
    A window just to show all the ErrorNodes.
    """
    def __init__(self, parent=None):
        super(LogWin, self).__init__(parent)
        self.setupUi(self)
        self.listWidget.itemClicked.connect(self.selectNode)

    def populateUi(self, itmList):
        """
        just put all the passed errorNodes into the listWidget.
        :return:
        :rtype:
        """
        for each in itmList:
            self.listWidget.addItems(each)
        pass

    def selectNode(self):
        """
        This is to select the ErrorNodes in Maya.
        :return:
        :rtype:
        """
        itm = self.listWidget.selectedItems()[0]
        mayaNode = ''
        if itm:
            mayaNode = itm.text()
        if mayaNode:
            pm.select(mayaNode)


def main():
    """
    This is to call the Main UI.
    :return:
    :rtype:
    """
    import sys
    make_app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    main_form = Validator(debug=False)  # We set the form to be our ExampleApp (design)
    main_form.show()  # Show the form
    # return main_form
    return make_app.exec_()  # and execute the app


if __name__ == '__main__':
    a = main()
