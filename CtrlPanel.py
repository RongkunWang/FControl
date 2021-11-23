from functools import partial


from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QSizePolicy,
        QCheckBox)

import db
from OpcFlxRelation import OpcFlxRelation


class CtrlPanel(QWidget, OpcFlxRelation):
    def __init__(self, det = "MM", side = 0):
        QWidget.__init__(self)
        OpcFlxRelation.__init__(self)

        self.ncolflx = 3
        self.ncolopc = 3
        self.ncol = self.ncolflx + self.ncolopc  

        self.l_flx_cb     = []
        self.l_flx_but    = []
        self.l_flxlog_but = []

        self.l_opc_cb     = []
        self.l_opc_but    = []
        self.l_opclog_but = []



        for sector, l_flx in db.flx_dict[det].items():
            self.opc_flx(sector, l_flx, db.port_dict[det][sector])

        # global buttons
        self.layout_main = QGridLayout(self)
        self.but_init_all = QPushButton("flx-init all felix")
        self.layout_main.addWidget(self.but_init_all, 0, 0, 1, 1)
        self.but_restart_failed = QPushButton("Restart Failed Servers")
        self.layout_main.addWidget(self.but_restart_failed, 0, 1, 1, 1)
        self.but_clear_cache = QPushButton("Clear Cache(potentially large!)")
        self.layout_main.addWidget(self.but_clear_cache, 0, 5, 1, 1)

        self.cb_all_flx = QCheckBox("All felix")
        self.layout_main.addWidget(self.cb_all_flx, 1, 0, 1, 1)
        self.but_start_all_selected_flx = QPushButton("Start checked felixcore")
        self.layout_main.addWidget(self.but_start_all_selected_flx, 1, 1, 1, 1)
        self.but_stop_all_selected_flx = QPushButton("Stop checked felixcore")
        self.layout_main.addWidget(self.but_stop_all_selected_flx, 1, 2, 1, 1)

        self.cb_all_opc = QCheckBox("All opc")
        self.layout_main.addWidget(self.cb_all_opc, 1, self.ncolflx, 1, 1)
        self.but_start_all_selected_opc = QPushButton("Start checked opc")
        self.layout_main.addWidget(self.but_start_all_selected_opc, 1, self.ncolflx + 1, 1, 1)
        self.but_stop_all_selected_opc = QPushButton("Stop checked opc")
        self.layout_main.addWidget(self.but_stop_all_selected_opc, 1, self.ncolflx + 2, 1, 1)

        # individual buttons
        self.layout_but = QGridLayout()
        self.layout_main.addLayout(self.layout_but, 2, 0, 1, self.ncol)

        nrow = 0
        for i, flx in enumerate(self.return_list_flx()[side]):
            rowspan = len(self.kill_chain_flx(flx)[1])

            # checkbox for run all
            cb = QCheckBox(flx)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            cb.setObjectName(flx)
            self.l_flx_cb.append( cb )
            self.layout_but.addWidget( self.l_flx_cb[-1], nrow, 0, rowspan, 1)

            # this button is for running server(individually)
            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_but.append( but )
            but.setText("run server")
            but.setObjectName(flx)
            self.layout_but.addWidget( self.l_flx_but[-1], nrow, 1, rowspan, 1)

            # this button is for checking log(individually)
            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flxlog_but.append( but )
            but.setText("Check Log")
            but.setObjectName(flx)
            self.layout_but.addWidget( self.l_flxlog_but[-1], nrow, 2, rowspan, 1)

            nrow += rowspan

        nrow = 0
        for i, sector in enumerate(self.return_list_opc()[side]):
            rowspan = len(self.d_opc_flx[sector])

            cb = QCheckBox("Opc " + sector)
            cb.setObjectName(sector)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_cb.append( cb )
            self.layout_but.addWidget( self.l_opc_cb[-1], nrow, self.ncolflx, rowspan, 1)

            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setText("Run Server")
            but.setObjectName(sector)
            self.l_opc_but.append( but )
            self.layout_but.addWidget( self.l_opc_but[-1], nrow, self.ncolflx + 1, rowspan, 1)

            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setText("Check Log")
            but.setObjectName(sector)
            self.l_opclog_but.append( but )
            self.layout_but.addWidget( self.l_opclog_but[-1], nrow, self.ncolflx + 2, rowspan, 1)


            nrow += rowspan
            pass

        self.set_signal()
        pass


    def set_signal(self):
        self.set_cb_relationship()
        pass

    def set_cb_relationship(self,):
        self.cb_all_flx.stateChanged.connect(partial(self.toggle_checkbox, self.l_flx_cb))
        self.cb_all_opc.stateChanged.connect(partial(self.toggle_checkbox, self.l_opc_cb))
        for cb in self.l_opc_cb:
            l_cb_flx = []
            for flx in self.d_opc_flx[cb.objectName()]:
                for flx_cb in self.l_flx_cb:
                    if flx == flx_cb.objectName():
                        l_cb_flx.append(flx_cb)
            cb.stateChanged.connect(partial(self.toggle_flx_checkbox, l_cb_flx))
        for cb in self.l_flx_cb:
            l_cb_opc = []
            for opc in self.d_flx_opc[cb.objectName()]:
                for opc_cb in self.l_opc_cb:
                    if opc == opc_cb.objectName():
                        l_cb_opc.append(opc_cb)
            cb.stateChanged.connect(partial(self.toggle_opc_checkbox, l_cb_opc))

    @QtCore.pyqtSlot(int)
    def toggle_checkbox(self, l_cb, state):
        for cb in l_cb:
            cb.setCheckState(state)

    @QtCore.pyqtSlot(int)
    def toggle_flx_checkbox(self, l_cb, state):
        if state == 2:
            for cb in l_cb:
                cb.setCheckState(state)
            pass
        pass

    @QtCore.pyqtSlot(int)
    def toggle_opc_checkbox(self, l_cb, state):
        if state == 0:
            for cb in l_cb:
                cb.setCheckState(state)
            pass
        pass

    def quit(self):
        pass

    pass

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    m = CtrlPanel()
    print()
    print(m.kill_chain_flx("pc-tdq-flx-nsw-mm-00.cern.ch"))
    print(m.restart_chain_opc("A03"))
