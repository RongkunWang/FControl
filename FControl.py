#!/usr/bin/env python3

import sys, signal

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from MainWindow import MainWindow
from git_version import git_version

class Execute(QApplication):
    def __init__(self, git_tag, *argv):
        QApplication.__init__(self, sys.argv)
        self._win = MainWindow(git_tag)

        QtCore.QCoreApplication.instance().installEventFilter(self)
        pass

    def eventFilter(self, target, event):
        # Esc to close
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self._win.closeEvent(event)
                # TODO: can be done better?
                return True
        return super(QApplication, self).eventFilter(target, event)

    def quit(self):
        self._win.closeEvent(QtCore.QEvent(QtCore.QEvent.Close))

if __name__ == '__main__':
    app = Execute(git_version(), sys.argv)

    def sigint_handler(*args):
        print("\nCtrl+C pressed. Closing.") 
        app.quit()
        pass
    def sigquit_handler(*args):
        print("\nCtrl+\ pressed. Closing")
        app.quit()
        pass

    signal.signal(signal.SIGINT,  sigint_handler)
    signal.signal(signal.SIGQUIT, sigquit_handler)
    timer = QtCore.QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec_())
