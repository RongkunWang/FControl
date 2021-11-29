from functools import partial
import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QSizePolicy,
        QCheckBox, QMessageBox)

import db, utilities
from OpcFlxRelation import OpcFlxRelation
from CommandSender import CommandSender



USER = os.environ["USER"]

class CtrlPanel(QWidget, OpcFlxRelation):
    def __init__(self, det = "MM", side = 0):
        sside = "C" if side else "A"
        QWidget.__init__(self)
        OpcFlxRelation.__init__(self)

        self.cs = CommandSender(f"/shared/data/{USER}/FControl/{det}-{sside}")
        self.det = det

        self.ncolflx = 5
        self.ncolopc = 4
        self.ncol = self.ncolflx + self.ncolopc  

        self.l_flx_cb      = {}
        self.l_flx_ini_but = {}
        self.l_flx_run_but = {}
        self.l_flx_stp_but = {}
        self.l_flx_log_but  = {}

        self.l_opc_cb      = {}
        self.l_opc_run_but = {}
        self.l_opc_stp_but = {}
        self.l_opc_log_but  = {}

        for sector, l_flx in db.flx_dict[self.det].items():
            if (side == 0 and "C" in sector) or (side == 1 and "A" in sector):
                continue
            self.add_opc_flx(sector, l_flx)

        # global buttons
        self.layout_main = QGridLayout(self)
        self.layout_but = QGridLayout()
        self.layout_main.addLayout(self.layout_but, 2, 0, 1, self.ncol)

        self.but_init_all = QPushButton("flx-init all felix")
        self.but_init_all.setEnabled(False)
        utilities.set_default_button_color( self.but_init_all.palette() )
        self.but_init_all.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_init_all, 0, 0, 1, 1)

        self.but_kill_failed = QPushButton("Kill Failed Servers")
        self.but_kill_failed.setEnabled(False)
        self.but_kill_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_kill_failed, 0, 1, 1, 1)

        self.but_restart_failed = QPushButton("Restart Failed Servers")
        self.but_restart_failed.setEnabled(False)
        self.but_restart_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_restart_failed, 0, 2, 1, 1)

        self.but_clear_cache = QPushButton("Clear Cache(potentially large!)")
        self.but_clear_cache.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_clear_cache, 0, self.ncol - 1, 1, 1)
        self.but_clear_cache.clicked.connect(partial(self.cs.delete_all_log))

        self.cb_all_flx = QCheckBox("All felix")
        self.cb_all_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_flx, 0, 0, 1, 1)
        self.but_init_all_selected_flx = QPushButton("Init checked flx")
        self.but_init_all_selected_flx.setEnabled(False)
        self.but_init_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_init_all_selected_flx, 0, 1, 1, 1)
        self.but_start_all_selected_flx = QPushButton("Start checked servers")
        self.but_start_all_selected_flx.setEnabled(False)
        self.but_start_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_flx, 0, 2, 1, 1)
        self.but_stop_all_selected_flx = QPushButton("Stop checked servers")
        self.but_stop_all_selected_flx.setEnabled(False)
        self.but_stop_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_stop_all_selected_flx, 0, 3, 1, 1)

        self.but_check_all_selected_flx = QPushButton("Check felix link")
        self.but_check_all_selected_flx.setEnabled(False)
        self.but_check_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_check_all_selected_flx, 0, 4, 1, 1)

        self.cb_all_opc = QCheckBox("All opc")
        self.cb_all_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_opc, 0, self.ncolflx, 1, 1)
        self.but_start_all_selected_opc = QPushButton("Start checked opc")
        self.but_start_all_selected_opc.setEnabled(False)
        self.but_start_all_selected_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_opc, 0, self.ncolflx + 1, 1, 1)
        self.but_stop_all_selected_opc = QPushButton("Stop checked opc")
        self.but_stop_all_selected_opc.setEnabled(False)
        self.but_stop_all_selected_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_stop_all_selected_opc, 0, self.ncolflx + 2, 1, 1)

        # individual buttons
        nrow = 1
        for flx, server in self.return_list_flx().items():
            server.cs = self.cs
            #  server.init_jobname = self.init_flx_jobname(flx)
            #  server.run_jobname = self.flx_jobname(flx)

            rowspan = len(self.kill_chain_flx(flx)[1])

            # checkbox for run all
            cb = QCheckBox(flx)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_cb[flx] = cb 
            self.layout_but.addWidget( self.l_flx_cb[flx], nrow, 0, rowspan, 1)
            server.checkbox = cb

            # this button is for initializing server(individually)
            but = QPushButton("init felix")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_ini_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_ini_but[flx], nrow, 1, rowspan, 1)
            but.clicked.connect(partial(server.init))
            server.init_ind = but
            server.init_controller = but

            # this button is for running server(individually)
            but = QPushButton("run server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_run_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_run_but[flx], nrow, 2, rowspan, 1)
            but.clicked.connect(partial(server.run), QtCore.Qt.UniqueConnection | QtCore.Qt.QueuedConnection)
            server.run_controller = but

            # this button is for running server(individually)
            but = QPushButton("stop server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_stp_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_stp_but[flx], nrow, 3, rowspan, 1)
            but.clicked.connect(partial(server.stop))
            server.stop_controller = but

            # this button is for checking log(individually)
            but = QPushButton("check log")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_log_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_log_but[flx], nrow, 4, rowspan, 1)
            but.clicked.connect(partial(server.log))
            server.run_ind = but

            nrow += rowspan

        nrow = 1
        for sector, server in self.return_list_opc().items():
            server.set_commands(self.det, sector)
            server.cs = self.cs
            #  server.run_jobname = self.opc_jobname(sector)

            rowspan = len(server.l_flx)

            cb = QCheckBox("Opc " + sector)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_cb[sector] = cb 
            self.layout_but.addWidget( self.l_opc_cb[sector], nrow, self.ncolflx, rowspan, 1)
            server.checkbox = cb

            but = QPushButton("run server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_run_but[sector] = but 
            self.layout_but.addWidget( self.l_opc_run_but[sector], nrow, self.ncolflx + 1, rowspan, 1)
            but.clicked.connect(partial(server.run))
            server.init_ind = but
            server.run_controller = but

            but = QPushButton("stop server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_stp_but[sector] =  but 
            self.layout_but.addWidget( self.l_opc_stp_but[sector], nrow, self.ncolflx + 2, rowspan, 1)
            but.clicked.connect(partial(server.stop))
            server.stop_controller = but

            but = QPushButton("check log")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_log_but[sector] =  but 
            self.layout_but.addWidget( self.l_opc_log_but[sector], nrow, self.ncolflx + 3, rowspan, 1)
            but.clicked.connect(partial(server.log))
            server.run_ind = but

            nrow += rowspan
            pass

        self.set_signal()
        pass

    # Functionality
    #  def flx_jobname(self, flx):
        #  return f"felixcore_{flx}"

    #  def init_flx_jobname(self, flx):
        #  return f"init_{flx}"

    #  def opc_jobname(self, sector):
        #  return f"opc_{sector}"

    def set_signal(self):
        self.set_cb_relationship()
        self.set_button()
        pass

    def set_button(self,):
        pass

    def set_cb_relationship(self,):
        def toggle_checkbox(l_cb, state):
            for cb in l_cb:
                cb.setCheckState(state)
        self.cb_all_flx.stateChanged.connect(partial(toggle_checkbox, self.l_flx_cb.values()))
        self.cb_all_opc.stateChanged.connect(partial(toggle_checkbox, self.l_opc_cb.values()))

        @QtCore.pyqtSlot(int)
        def toggle_opc_checkbox(flx, l_cb, state):
            """
            act upon flx checkbox
            if flx is 0(off), turn off opc, too
            """
            self.l_flx[flx].set_enable_state()
            if state == 2: return
            for cb in l_cb:
                cb.setCheckState(state)
            pass
        for name, cb in self.l_flx_cb.items():
            l_cb_opc = []
            for opc in self.l_flx[name].l_opc:
                l_cb_opc.append(self.l_opc_cb[opc])
            cb.stateChanged.connect(partial(toggle_opc_checkbox, name, l_cb_opc))

        @QtCore.pyqtSlot(int)
        def toggle_flx_checkbox(opc, l_cb, state):
            """
            act upon opc checkbox
            if opc is 2(on), turn on felix, too
            """
            self.l_opc[opc].set_enable_state()
            if state == 0: return
            for cb in l_cb:
                cb.setCheckState(state)
        for name, cb in self.l_opc_cb.items():
            l_flx_cb = []
            for flx in self.l_opc[name].l_flx:
                l_flx_cb.append(self.l_flx_cb[flx])
            cb.stateChanged.connect(partial(toggle_flx_checkbox, name, l_flx_cb))



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