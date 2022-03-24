from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextBrowser

class LogChecker(QWidget):
    """
    the log checker window for log()
    """
    closed = pyqtSignal()
    def __init__(self, logname):
        super(LogChecker, self).__init__()
        self.resize(1200, 800)
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
