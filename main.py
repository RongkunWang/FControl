#!/usr/bin/env python3

import sys, string, random, os, fileinput

from PyQt5.QtWidgets import QApplication

from main_window import main_window

class Execute():
    def __init__(self):
        self._win = main_window()
        pass
    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    exe = Execute()
    sys.exit(app.exec_())
    pass
