import functools
import shiboken
from PySide import QtCore
from PySide import QtGui

import maya.OpenMayaUI
import pymel.core as pm


def _display_message(status, message):
    status_colors = {
        # status    gradientStart      gradientEnd          text
        'internal failure': ((255, 111, 105), (255, 111, 105), (0, 0, 0)),
        'fatal': ((255, 40, 20), (255, 40, 20), (0, 0, 0)),
        'warning': ((255, 177, 86), (255, 177, 86), (0, 0, 0)),
        'success': ((140, 230, 140), (140, 230, 140), (0, 0, 0)),
        'null': ((127, 127, 127), (127, 127, 127), (0, 0, 0))
    }

    # Recover the 'commandLine' QSplitter (its MayaUI name is always 'commandLine1')
    # noinspection PyCallByClass,PyTypeChecker
    command_line_ptr = maya.OpenMayaUI.MQtUtil.findControl('commandLine1')
    command_line = shiboken.wrapInstance(long(command_line_ptr), QtGui.QSplitter)

    # The 0th one is the messageLine (a <QLineEdit>)
    result_line = command_line.findChildren(QtGui.QLineEdit)[0]

    # Set the message
    # E.g. "[APOCALYPSE] Maya hates you (because probably you code sucks...)!")    
    result_line.setText('[' + status.upper() + '] ' + message)

    # Customize colors (temporarily via a palette, not via a setStyleSheet which is permanent)
    """ I would like an HORIZONTAL_GRADIENT and RICH_TEXT"""
    palette = result_line.palette()
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(0, 0, 0))
    palette = result_line.palette()
    gradient = QtGui.QLinearGradient(QtCore.QRectF(result_line.rect()).topLeft(),
                                     QtCore.QRectF(result_line.rect()).topRight())
    gradient.setColorAt(0.0, QtGui.QColor(*status_colors[status][0]))
    gradient.setColorAt(1.0, QtGui.QColor(*status_colors[status][1]))
    palette.setBrush(QtGui.QPalette.Base, QtGui.QBrush(gradient))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(*status_colors[status][2]))
    result_line.setPalette(palette)
    pm.refresh()


displayInternalFailure = functools.partial(_display_message, 'internal failure')
displayFatal = functools.partial(_display_message, 'fatal')
displayWarning = functools.partial(_display_message, 'warning')
displaySuccess = functools.partial(_display_message, 'success')
displayNull = functools.partial(_display_message, 'null')


if __name__ == '__main__':
    msg = 'Durgesh Kalyan Nayak'
    displayInternalFailure(msg)
    displayFatal(msg)
    displayWarning(msg)
    displaySuccess(msg)
    displayNull(msg)
