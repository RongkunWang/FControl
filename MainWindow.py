from PyQt5.QtWidgets import  QTabWidget, QMainWindow, QApplication
from PyQt5 import  QtCore

from CtrlPanel import CtrlPanel

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


        self.setWindowTitle("FControl")
        self.resize(1400, 900)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.MMA = CtrlPanel()
        self.tabs.addTab(self.MMA, "MM-A")

        self.MMC = CtrlPanel("MM", 1)
        self.tabs.addTab(self.MMC, "MM-C")

        self.sTGCA = CtrlPanel("sTGC")
        self.tabs.addTab(self.sTGCA, "sTGC-A")

        self.sTGCC = CtrlPanel("sTGC", 1)
        self.tabs.addTab(self.sTGCC, "sTGC-C")

        self.show()
        pass


    def closeEvent(self, event):
        print("FControl exiting gracefully")
        self.MMA.quit()
        self.MMC.quit()
        self.sTGCA.quit()
        self.sTGCC.quit()
        event.accept()
        QApplication.quit()
        # TODO: can ask if yes or not!
        #  return True
    pass
