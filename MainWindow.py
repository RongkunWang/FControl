from functools import partial

from PyQt5.QtWidgets import  QTabBar, QTabWidget, QMainWindow, QApplication, QWidget, QStyle, QStylePainter, QStyleOptionTab
from PyQt5 import  QtCore
from PyQt5.QtGui import QPalette, QPaintEvent

from CtrlPanel import CtrlPanel
from TPCtrlPanel import TPCtrlPanel

class MainWindow(QMainWindow):
    class specialTabBar(QTabBar):
        def __init__(self, *args):
            super().__init__(*args)
            self.d_color = {}
            #  self.opt = QStyleOptionTab()
            #  self.painter = QStylePainter(self)
            pass

        def paintEvent(self, paint_event):
            #  self.m_pe = paint_event
            self.m_pereg = paint_event.region()
            #  print(paint_event.region())
            #  print(self.d_color)
            painter = QStylePainter(self)
            #  l_opt = [] 
            opt = QStyleOptionTab()
            for i in range(self.count()):
                #  print(i)
                #  l_opt.append(QStyleOptionTab())
                #  self.initStyleOption(l_opt[i], i);
                #  self.initStyleOption(self.opt, i);
                self.initStyleOption(opt, i);
                if i in self.d_color:
                    opt.palette.setColor(QPalette.Button, self.d_color[i])
                painter.drawControl(QStyle.CE_TabBarTabShape, opt)
                painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            pass
        pass

    class specialTabWidget(QTabWidget):
        def __init__(self, *args):
            super().__init__(*args)
            self._tabBar = QTabBar(self)
            self.setTabBar(self._tabBar)
            pass


        
        #  def paint(self, idx, color):
            #  QStylePainter painter(this);

        #  @property
        #  def tabBar(self):
            #  return self._tabBar 
        pass

    def __init__(self, title):
        QMainWindow.__init__(self)

        self.setWindowTitle(f"FControl - {title}")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        #  self.tabs = MainWindow.specialTabWidget()
        #  bar = MainWindow.specialTabBar()
        self.tabs.setTabBar(MainWindow.specialTabBar())
        #  self.tabs.setTabShape(QTabWidget.Triangular)
        self.setCentralWidget(self.tabs)

        #  self.tabs.set

        self.MMA = CtrlPanel(self,)
        self.MMA.serverStatus.connect(partial(self.update_server_status))
        self.tabs.addTab(self.MMA, "MM-A")
        #  self.tabs.tabBar().setTabTextColor(0, QtCore.Qt.green)
        #  self.tabs.tabBar().setStyleSheet("QWidget { background-color:cyan; }");

        self.MMC = CtrlPanel(self, "MM", 2)
        self.MMC.serverStatus.connect(partial(self.update_server_status))
        self.tabs.addTab(self.MMC, "MM-C")

        self.sTGCA = CtrlPanel(self, "sTGC")
        self.sTGCA.serverStatus.connect(partial(self.update_server_status))
        self.tabs.addTab(self.sTGCA, "sTGC-A")

        self.sTGCC = CtrlPanel(self, "sTGC", 2)
        self.sTGCC.serverStatus.connect(partial(self.update_server_status))
        self.tabs.addTab(self.sTGCC, "sTGC-C")

        self.TP = TPCtrlPanel(self, "TP", 3, False)
        self.TP.serverStatus.connect(partial(self.update_server_status))
        self.tabs.addTab(self.TP, "TP")

        self.show()
        pass

    @QtCore.pyqtSlot(int)
    def update_server_status(self, status):
        idx = self.tabs.indexOf(self.sender())
        if status == 0:
            # for some reason multiple 0 signal is emitted, catch here
            if idx in self.tabs.tabBar().d_color:
                self.tabs.tabBar().d_color.pop(idx)
        elif status == 1:
            self.tabs.tabBar().d_color[idx] = QtCore.Qt.green
        elif status == 2:
            self.tabs.tabBar().d_color[idx] = QtCore.Qt.yellow
        elif status == 3:
            self.tabs.tabBar().d_color[idx] = QtCore.Qt.red
        # should call paintEvent
        self.tabs.tabBar().update()
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
