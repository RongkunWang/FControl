from PyQt5.QtWidgets import  QTabWidget, QMainWindow, QApplication
from PyQt5 import  QtCore

from CtrlPanel import CtrlPanel
from TPCtrlPanel import TPCtrlPanel

class MainWindow(QMainWindow):
    def __init__(self, title):
        QMainWindow.__init__(self)


        self.setWindowTitle(f"FControl - {title}")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.MMA = CtrlPanel(self,)
        self.tabs.addTab(self.MMA, "MM-A")

        self.MMC = CtrlPanel(self, "MM", 2)
        self.tabs.addTab(self.MMC, "MM-C")

        self.sTGCA = CtrlPanel(self, "sTGC")
        self.tabs.addTab(self.sTGCA, "sTGC-A")

        self.sTGCC = CtrlPanel(self, "sTGC", 2)
        self.tabs.addTab(self.sTGCC, "sTGC-C")

        self.TP = TPCtrlPanel(self, "TP", 3, False)
        self.tabs.addTab(self.TP, "TP")

        self.show()
        pass


    def closeEvent(self, event):
        print("FControl exiting gracefully")
        self.MMA.quit()
        self.MMC.quit()
        self.sTGCA.quit()
        self.sTGCC.quit()
        self.TP.quit()

        event.accept()
        QApplication.quit()
        # TODO: can ask if yes or not!
    pass
