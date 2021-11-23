from functools import partial


from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QSizePolicy,
        QCheckBox, QSpacerItem)

import db, os
from OpcFlxRelation import OpcFlxRelation
from CommandSender import CommandSender

USER = os.environ["USER"]

class CtrlPanel(QWidget, OpcFlxRelation):
    def __init__(self, det = "MM", side = 0):
        sside = "C" if side else "A"
        QWidget.__init__(self)
        OpcFlxRelation.__init__(self)

        self.cs = CommandSender(f"/tmp/rowang/{det}-{sside}")

        self.ncolflx = 4
        self.ncolopc = 4
        self.ncol = self.ncolflx + self.ncolopc  

        self.l_flx_cb      = []
        self.l_flx_run_but = {}
        self.l_flx_stp_but = {}
        self.l_flxlog_but  = []

        self.l_opc_cb     = []
        self.l_opc_but    = []
        self.l_opclog_but = []



        for sector, l_flx in db.flx_dict[det].items():
            if (side == 0 and "C" in sector) or (side == 1 and "A" in sector):
                continue
            self.add_opc_flx(sector, l_flx, db.port_dict[det][sector])

        # global buttons
        self.layout_main = QGridLayout(self)
        self.layout_but = QGridLayout()
        self.layout_main.addLayout(self.layout_but, 2, 0, 1, self.ncol)

        self.but_init_all = QPushButton("flx-init all felix")
        self.but_init_all.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_init_all, 0, 0, 1, 1)
        self.but_restart_failed = QPushButton("Restart Failed Servers")
        self.but_restart_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_restart_failed, 0, 1, 1, 1)
        self.but_clear_cache = QPushButton("Clear Cache(potentially large!)")
        self.but_clear_cache.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_clear_cache, 0, self.ncol - 1, 1, 1)

        self.cb_all_flx = QCheckBox("All felix")
        self.cb_all_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_flx, 0, 0, 1, 1)
        self.but_start_all_selected_flx = QPushButton("Start checked felixcore")
        self.but_start_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_flx, 0, 1, 1, 1)
        self.but_stop_all_selected_flx = QPushButton("Stop checked felixcore")
        self.but_stop_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_stop_all_selected_flx, 0, 2, 1, 1)
        #  self.layout_but.addItem(QSpacerItem(1, 1, 
            #  QSizePolicy.Expanding, 
            #  QSizePolicy.Fixed), 1, 3, 1, 1)


        self.cb_all_opc = QCheckBox("All opc")
        self.cb_all_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_opc, 0, self.ncolflx, 1, 1)
        self.but_start_all_selected_opc = QPushButton("Start checked opc")
        self.but_start_all_selected_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_opc, 0, self.ncolflx + 1, 1, 1)
        self.but_stop_all_selected_opc = QPushButton("Stop checked opc")
        self.but_stop_all_selected_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_stop_all_selected_opc, 0, self.ncolflx + 2, 1, 1)
        #  self.layout_but.setColumnStretch(self.ncolflx + 3, 1)

        # individual buttons

        nrow = 1
        for flx in self.return_list_flx():
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
            self.l_flx_run_but[flx] =  but 
            but.setText("run server")
            but.setObjectName(flx)
            self.layout_but.addWidget( self.l_flx_run_but[flx], nrow, 1, rowspan, 1)

            but = QPushButton("stop server")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_stp_but[flx] =  but 
            but.setObjectName(flx)
            self.layout_but.addWidget( self.l_flx_stp_but[flx], nrow, 2, rowspan, 1)

            # this button is for checking log(individually)
            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flxlog_but.append( but )
            but.setText("check log")
            but.setObjectName(flx)
            self.layout_but.addWidget( self.l_flxlog_but[-1], nrow, 3, rowspan, 1)

            nrow += rowspan

        nrow = 1
        for sector in self.return_list_opc():
            rowspan = len(self.d_opc_flx[sector])

            cb = QCheckBox("Opc " + sector)
            cb.setObjectName(sector)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_cb.append( cb )
            self.layout_but.addWidget( self.l_opc_cb[-1], nrow, self.ncolflx, rowspan, 1)

            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setText("run server")
            but.setObjectName(sector)
            self.l_opc_but.append( but )
            self.layout_but.addWidget( self.l_opc_but[-1], nrow, self.ncolflx + 1, rowspan, 1)


            but = QPushButton("stop server")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setObjectName(sector)
            self.l_opc_but.append( but )
            self.layout_but.addWidget( self.l_opc_but[-1], nrow, self.ncolflx + 2, rowspan, 1)

            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setText("check log")
            but.setObjectName(sector)
            self.l_opclog_but.append( but )
            self.layout_but.addWidget( self.l_opclog_but[-1], nrow, self.ncolflx + 3, rowspan, 1)


            nrow += rowspan
            pass

        self.set_signal()
        pass


    def set_signal(self):
        self.set_cb_relationship()
        self.set_button()
        pass

    def set_button(self,):
        for flx_host, b in self.l_flx_run_but.items():
            b.clicked.connect(partial(self.run_flx_server, flx_host))
            pass

        for flx_host, b in self.l_flx_stp_but.items():
            b.clicked.connect(partial(self.stop_flx_server, flx_host))
            b.setEnabled(False)
            pass
        pass

    @QtCore.pyqtSlot(str)
    def run_flx_server(self, flx_host):
        self.l_flx_stp_but[flx_host].setEnabled(True)
        self.l_flx_run_but[flx_host].setEnabled(False)
        self.cs.send_command(flx_host, flx_host, flx_host,
                f"{db.FLX_SETUP} && {self.exe_flx} {db.flx_arg[flx_host]}")
        pass

    @QtCore.pyqtSlot(str)
    def stop_flx_server(self, flx_host):
        self.l_flx_stp_but[flx_host].setEnabled(False)
        self.l_flx_run_but[flx_host].setEnabled(True)
        self.cs.stop_command(flx_host)
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
        self.cs.stop_all()
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
