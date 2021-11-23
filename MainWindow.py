from PyQt5.QtWidgets import  QTabWidget, QMainWindow, qApp
from PyQt5 import  QtCore

from CtrlPanel import CtrlPanel
from sTGC import sTGC

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

    #  def eventFilter(self, target, event):
        #  # Esc to close
        #  if event.type() == QtCore.QEvent.KeyPress:
            #  if event.key() == QtCore.Qt.Key_Escape:
                #  self.exit_sequence()

        #  return super(MainWindow, self).eventFilter(target, event)


    def quit(self, ):
        self.MMA.quit()
        self.MMC.quit()
        self.sTGCA.quit()
        self.sTGCC.quit()
        self.close()

    pass
