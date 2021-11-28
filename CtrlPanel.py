from functools import partial


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QSizePolicy,
        QCheckBox, QMessageBox, QTextEdit)

import db, os
from OpcFlxRelation import OpcFlxRelation
from CommandSender import CommandSender

USER = os.environ["USER"]

class CtrlPanel(QWidget, OpcFlxRelation):
    def __init__(self, det = "MM", side = 0):
        sside = "C" if side else "A"
        QWidget.__init__(self)
        OpcFlxRelation.__init__(self)

        #  self.log_dir = f"/shared/data/{USER}{det}-{sside}"
        self.cs = CommandSender(f"/shared/data/{USER}/{det}-{sside}")
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



        for sector, l_flx in db.flx_dict[det].items():
            if (side == 0 and "C" in sector) or (side == 1 and "A" in sector):
                continue
            self.add_opc_flx(sector, l_flx)

        # global buttons
        self.layout_main = QGridLayout(self)
        self.layout_but = QGridLayout()
        self.layout_main.addLayout(self.layout_but, 2, 0, 1, self.ncol)

        self.but_init_all = QPushButton("flx-init all felix")
        self.but_init_all.setEnabled(False)
        self._default_button_pal = self.but_init_all.palette()
        self.but_init_all.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_init_all, 0, 0, 1, 1)
        self.but_restart_failed = QPushButton("Restart Failed Servers")
        self.but_restart_failed.setEnabled(False)
        self.but_restart_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_restart_failed, 0, 1, 1, 1)
        self.but_kill_failed = QPushButton("Kill Failed Servers")
        self.but_kill_failed.setEnabled(False)
        self.but_kill_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_kill_failed, 0, 2, 1, 1)
        self.but_clear_cache = QPushButton("Clear Cache(potentially large!)")
        self.but_clear_cache.setEnabled(False)
        self.but_clear_cache.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_clear_cache, 0, self.ncol - 1, 1, 1)

        self.cb_all_flx = QCheckBox("All felix")
        self.cb_all_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_flx, 0, 0, 1, 1)
        self.but_init_all_selected_flx = QPushButton("Init checked felixcore")
        self.but_init_all_selected_flx.setEnabled(False)
        self.but_init_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_init_all_selected_flx, 0, 1, 1, 1)
        self.but_start_all_selected_flx = QPushButton("Start checked felixcore")
        self.but_start_all_selected_flx.setEnabled(False)
        self.but_start_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_flx, 0, 2, 1, 1)
        self.but_stop_all_selected_flx = QPushButton("Stop checked felixcore")
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
        for flx in self.return_list_flx():
            rowspan = len(self.kill_chain_flx(flx)[1])

            # checkbox for run all
            cb = QCheckBox(flx)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_cb[flx] = cb 
            self.layout_but.addWidget( self.l_flx_cb[flx], nrow, 0, rowspan, 1)

            but = QPushButton("init felix")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_ini_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_ini_but[flx], nrow, 1, rowspan, 1)

            # this button is for running server(individually)
            but = QPushButton("run server")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_run_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_run_but[flx], nrow, 2, rowspan, 1)


            # this button is for running server(individually)
            but = QPushButton("stop server")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_stp_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_stp_but[flx], nrow, 3, rowspan, 1)

            # this button is for checking log(individually)
            but = QPushButton("check log")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_log_but[flx] =  but 
            self.layout_but.addWidget( self.l_flx_log_but[flx], nrow, 4, rowspan, 1)

            nrow += rowspan

        nrow = 1
        for sector in self.return_list_opc():
            rowspan = len(self.d_opc_flx[sector])

            cb = QCheckBox("Opc " + sector)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_cb[sector] = cb 
            self.layout_but.addWidget( self.l_opc_cb[sector], nrow, self.ncolflx, rowspan, 1)

            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setText("run server")
            self.l_opc_run_but[sector] = but 
            self.layout_but.addWidget( self.l_opc_run_but[sector], nrow, self.ncolflx + 1, rowspan, 1)


            but = QPushButton("stop server")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_stp_but[sector] =  but 
            self.layout_but.addWidget( self.l_opc_stp_but[sector], nrow, self.ncolflx + 2, rowspan, 1)

            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            but.setText("check log")
            self.l_opc_log_but[sector] =  but 
            self.layout_but.addWidget( self.l_opc_log_but[sector], nrow, self.ncolflx + 3, rowspan, 1)

            nrow += rowspan
            pass

        self.set_signal()
        pass


    # Functionality

    def default_flx_log(self, flx):
        return self.cs.full_log(flx)
        #  return os.path.join(self.log_dir, flx)

    def default_opc_log(self, sector):
        return self.cs.full_log(f"opc{sector}")
        #  return os.path.join(self.log_dir, f"opc{sector}")


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

        for flx_host, b in self.l_flx_ini_but.items():
            b.clicked.connect(partial(self.ini_flx_server, flx_host))


        for flx_host, b in self.l_flx_log_but.items():
            self.set_button_color(b, QtCore.Qt.gray)
            b.clicked.connect(partial(self.check_log, flx_host, 
                self.default_flx_log(flx_host)))
            pass

        for sector, b in self.l_opc_run_but.items():
            b.clicked.connect(partial(self.run_opc_server, sector))
            pass

        for sector, b in self.l_opc_stp_but.items():
            b.clicked.connect(partial(self.stop_opc_server, sector))
            b.setEnabled(False)
            pass

        for sector, b in self.l_opc_log_but.items():
            self.set_button_color(b, QtCore.Qt.gray)
            b.clicked.connect(partial(self.check_log, sector, 
                self.default_opc_log(sector)))
            pass
        pass


    def set_button_color(self, button, color = -999):
        if color != -999:
            pal = button.palette()
            pal.setColor(QtGui.QPalette.Button, QtGui.QColor(color));
            button.setAutoFillBackground(True)
            button.setPalette(pal)
            button.update()
        else:
            button.setPalette(self._default_button_pal)
            button.update()
        pass

    @QtCore.pyqtSlot(str)
    def check_log(self, name, full_log):
        if not self.cs.has_job(name):
            #  not active job
            if os.path.isfile(full_log):
                ret = QMessageBox.question(self, "Found old log",
                        "No active job found, check old log file?", 
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes)
                if ret == QMessageBox.No:
                    return
            else:
                msgBox = QMessageBox.warning(self, "No log file", 
                        "No active job found and no log file.")
                return
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(full_log))
        pass

    def health_size(self, full_log):
        # TODO-1: check by checking file size every 3 second
        pass

    def health_flx(self, ):
        #  TODO: check last line
        "FelixCore Up and Running"
        pass

    def health_opc(self, ):
        #  TODO: check last 3 line
        pass

    @QtCore.pyqtSlot(str)
    def ini_flx_server(self, flx_host):
        job_name = f"init_{flx_host}"
        if self.cs.has_job(job_name):
            self.cs.stop_command(job_name)
        self.cs.send_command(job_name, job_name, flx_host,
                f"{db.FLX_SETUP} && flx-init && flx-init -c1")
        self.set_button_color(self.l_flx_ini_but[flx_host], QtCore.Qt.yellow)
        ## TODO-1: monitor itself
        pass

    def run_flx_server(self, flx_host):
        self.l_flx_stp_but[flx_host].setEnabled(True)
        self.l_flx_run_but[flx_host].setEnabled(False)
        self.set_button_color(self.l_flx_log_but[flx_host], QtCore.Qt.yellow)
        self.cs.send_command(flx_host, os.path.basename(self.default_flx_log(flx_host)), flx_host,
                f"{db.FLX_SETUP} && {db.FLX_EXE} {db.flx_arg[flx_host]}")
        pass

    @QtCore.pyqtSlot(str)
    def stop_flx_server(self, flx_host):
        self.l_flx_stp_but[flx_host].setEnabled(False)
        self.l_flx_run_but[flx_host].setEnabled(True)
        self.cs.stop_command(flx_host)
        pass

    @QtCore.pyqtSlot(str)
    def run_opc_server(self, sector):
        self.l_opc_stp_but[sector].setEnabled(True)
        self.l_opc_run_but[sector].setEnabled(False)
        self.set_button_color(self.l_opc_log_but[sector], QtCore.Qt.yellow)
        self.cs.send_command(sector, os.path.basename(self.default_opc_log(sector)), f"{self.d_opc_flx[sector][0]}",
                f"{db.OPC_EXE} {db.OpcPort(db.port_dict[self.det][sector])} {db.opc_dict[self.det][sector]}")
                #  f"{self.exe_opc} {db.opc_dict[self.det][sector]}")
        pass

    @QtCore.pyqtSlot(str)
    def stop_opc_server(self, sector):
        self.l_opc_stp_but[sector].setEnabled(False)
        self.l_opc_run_but[sector].setEnabled(True)
        self.cs.stop_command(sector)
        pass


    def set_cb_relationship(self,):
        self.cb_all_flx.stateChanged.connect(partial(self.toggle_checkbox, self.l_flx_cb))
        self.cb_all_opc.stateChanged.connect(partial(self.toggle_checkbox, self.l_opc_cb))
        for name, cb in self.l_opc_cb.items():
            l_cb_flx = []
            for flx in self.d_opc_flx[name]:
                l_cb_flx.append(self.l_flx_cb[flx])
            cb.stateChanged.connect(partial(self.toggle_flx_checkbox, l_cb_flx))
        for name, cb in self.l_flx_cb.items():
            l_cb_opc = []
            for opc in self.d_flx_opc[name]:
                l_cb_opc.append(self.l_opc_cb[opc])
            cb.stateChanged.connect(partial(self.toggle_opc_checkbox, l_cb_opc))

    @QtCore.pyqtSlot(int)
    def toggle_checkbox(self, l_cb, state):
        for cb in l_cb:
            cb.setCheckState(state)

    @QtCore.pyqtSlot(int)
    def toggle_flx_checkbox(self, l_cb, state):
        # if opc is 2(on), turn on felix, too
        if state == 2:
            for cb in l_cb:
                cb.setCheckState(state)
            pass
        pass

    @QtCore.pyqtSlot(int)
    def toggle_opc_checkbox(self, l_cb, state):
        # if flx is 0(off), turn off opc, too
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
