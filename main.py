#!/usr/bin/env python3

import sys, string, random, os, fileinput

from PyQt5.QtWidgets import QApplication
from PyQt5 import  QtCore

from MainWindow import MainWindow

import signal

class Execute(QApplication):
    def __init__(self, *argv):
        QApplication.__init__(self, sys.argv)
        self._win = MainWindow()

        QtCore.QCoreApplication.instance().installEventFilter(self)
        #  self.installEventFilter(self)

        pass

    def eventFilter(self, target, event):
        # Esc to close
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self.quit()
                return True
        return super(QApplication, self).eventFilter(target, event)


    def quit(self):
        print("FControl exiting gracefully")
        self._win.quit()

if __name__ == '__main__':
    app = Execute(sys.argv)
    def sigint_handler(*args):
        print("Ctrl+C or Ctrl+/ pressed") 
        app.quit()
        pass
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGQUIT, sigint_handler)
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)
    sys.exit(app.exec_())
    pass
