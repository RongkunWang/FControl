from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextBrowser

class LogChecker(QWidget):
    """
    the log checker window for log()
    """
    closed = pyqtSignal()
    def __init__(self, logname, par):
        parentPos = QPoint()
        while "builtin_function_or_method" not in str(par.parent.__class__):
            parentPos += par.pos()
            par = par.parent
        # do also for mainWindow
        parentPos += par.pos()
        print(parentPos.x(), parentPos.y())
        # to the right, and bottom
        parentPos += QPoint(200, 100)
        #  print(par.width())
        #  print(par.height())
        super(LogChecker, self).__init__()
        self.resize(1300, 800)
        self.move(parentPos)
        self.setWindowTitle(f"log {logname}")
        #  self._textLog
        self._textLog = QTextBrowser(self)
        font = QFont ("monospace")
        font.setPointSize(10)
        self._textLog.setCurrentFont(font)
        lay = QHBoxLayout(self)
        lay.addWidget(self._textLog)
        self.show()

    @property
    def textLog(self):
        return self._textLog

    def closeEvent(self, event): 
        self.closed.emit()
        pass
    pass
