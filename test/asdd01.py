from PySide import QtCore,QtGui
import sys
class ToolBarUI(QtGui.QWidget):
    def __init__(self,*args,**kwargs):
        super(ToolBarUI,self).__init__(*args,**kwargs)
        self.createActions()

        self.floatingToolBar()
        pass

    def sizeHint(self):
        return QtCore.QSize(65,45)

    def buttons(self):
        x,y=15,35
        self.btnVLay=QtGui.QVBoxLayout(self)
        self.setLayout(self.btnVLay)
        self.btnVLay.setContentsMargins(0,0,0,0)

        self.incSavbtn=QtGui.QPushButton("Save")
        self.incSavbtn.setMinimumSize(QtCore.QSize(x,y))
        self.emailbtn=QtGui.QPushButton("Email")
        self.emailbtn.setMinimumSize(QtCore.QSize(x,y))
        self.upldbtn=QtGui.QPushButton("Upload")
        self.upldbtn.setMinimumSize(QtCore.QSize(x,y))
        self.setPrjbtn=QtGui.QPushButton("Set Project")
        self.setPrjbtn.setMinimumSize(QtCore.QSize(x,y))
        self.setThumb=QtGui.QPushButton("Set thumb")
        self.setThumb.setMinimumSize(QtCore.QSize(x,y))
        self.shwMatbtn=QtGui.QPushButton("Show Material")
        self.shwMatbtn.setMinimumSize(QtCore.QSize(x,y))
        self.fixtexbtn=QtGui.QPushButton("Fix Texture Paths")
        self.fixtexbtn.setMinimumSize(QtCore.QSize(x,y))

        btns = [self.incSavbtn,self.emailbtn,self.upldbtn,self.setPrjbtn,self.setPrjbtn,self.setThumb,self.shwMatbtn,self.fixtexbtn]

        [self.btnVLay.addWidget(each) for each in btns]

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.addAction(self.emlSel)
        menu.addAction(self.emlScn)
        menu.addAction(self.emlBufr)
        # self.incSavbtn.setMenu(menu)
        # menu.exec_(self.emailbtn.mapToGlobal(QtCore.QPoint(0,0)))
        #menu.exec_(event.globalPos())
        menu.showEvent(self.emailbtn.contextMenuEvent)

    def createActions(self):
        # self.menu = QtGui.QMenu(self)
        self.emlSel = QtGui.QAction("Email Selected", self)
        self.emlScn = QtGui.QAction("Email this Scene", self)
        self.emlBufr = QtGui.QAction("Email Current Frame Buffer", self)


    def floatingToolBar(self):
        self.buttons()
        self.setLayout(self.btnVLay)
        self.show()
        pass

if __name__ =='__main__':

    app = QtGui.QApplication(sys.argv)

    win = ToolBarUI()
    win.show()
    sys.exit(app.exec_())