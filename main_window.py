from PyQt5.QtWidgets import  QTabWidget, QMainWindow
from MM import MM
from sTGC import sTGC

class main_window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("FControl")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.MM = MM()
        self.tabs.addTab(self.MM, "MM-A")

        self.MM = MM("MM", 1)
        self.tabs.addTab(self.MM, "MM-C")

        self.sTGC = MM("sTGC")
        self.tabs.addTab(self.sTGC, "sTGC-A")

        self.sTGC = MM("sTGC", 1)
        self.tabs.addTab(self.sTGC, "sTGC-C")

        self.show()
        pass
    pass
