from functools import partial
import codecs
import os, sys
sys.path.insert(1, "/atlas-home/1/aawhite/this")
import nsw_this
print("Using convenience module:", nsw_this.__file__)

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QSizePolicy,
        QCheckBox, QMessageBox, QComboBox)

import db, utilities
from OpcFlxRelation import OpcFlxRelation
from CommandSender import CommandSender
from LogChecker import LogChecker

USER = os.environ["USER"]

class CtrlPanel(QWidget, OpcFlxRelation):
    # stopped 0
    # stable 1
    # communicating 2
    # fatal 3
    serverStatus = QtCore.pyqtSignal(int)
    def __init__(self, parent, det = "MM", side = 1, do_mainlayout = True, 
            isTP = False):
        self.parent = parent
        self.det = det
        self.side = side
        self.isTP = isTP

        self.sside = "C" if (side == 2) else "A"
        if do_mainlayout:
            QWidget.__init__(self)
            self.layout_main = QGridLayout(self)
        OpcFlxRelation.__init__(self)

        self.cs = CommandSender(db.getLog(USER, det, self.sside))


        self.l_thread = {}
        self.l_worker = {}


        self.s_server_stable        = set()
        self.s_server_communicating = set()
        self.s_server_fatal         = set()

        self.l_flx_cb      = {}
        self.l_flx_ini_but = {}
        self.l_flx_run_but = {}
        self.l_flx_stp_but = {}
        self.l_flx_log_but  = {}

        self.l_opc_cb      = {}
        self.l_opc_run_but = {}
        self.l_opc_stp_but = {}
        self.l_opc_log_but  = {}

        self.add_all()

        #########################################
        # global buttons
        #########################################
        self.layout_but = QGridLayout()
        self.layout_main.addLayout(self.layout_but, 3, 0, 1, db.ncol)

        #  self.but_init_all = QPushButton("setup all selected felix")
        #  self.but_init_all.setEnabled(False)
        #  self.but_init_all.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        #  self.layout_main.addWidget(self.but_init_all, 0, 0, 1, 1)

        self.but_check_gbt_link = QPushButton("Check gbt-links")
        #  self.but_check_gbt_link.setEnabled(False)
        self.but_check_gbt_link.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_check_gbt_link, 0, 0, 1, 1)
        self.but_check_gbt_link.clicked.connect(partial(self.check_gbtx))
        
        self.but_kill_failed = QPushButton("Kill Failed Servers")
        self.but_kill_failed.setEnabled(False)
        self.but_kill_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_kill_failed, 0, 1, 1, 1)

        # necesssary!
        utilities.set_default_button_color( self.but_kill_failed.palette() )

        self.but_restart_failed = QPushButton("Restart Failed Servers")
        self.but_restart_failed.setEnabled(False)
        self.but_restart_failed.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_restart_failed, 0, 2, 1, 1)

        if not self.isTP:
            self.flx_init_type = QComboBox()
            self.flx_init_type_list = []
            self.flx_init_type.addItem("init flx: sca_only")
            self.flx_init_type_list.append("supervisorctl start sca_only:*")
            self.flx_init_type.addItem("init flx: gbt")
            self.flx_init_type_list.append("supervisorctl start gbt:*")
            self.layout_main.addWidget(self.flx_init_type, 1, 0, 1, 1)
        
        self.but_check_server = QPushButton("Check Server Status(manual now)")
        self.but_check_server.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_check_server, 0, db.ncol - 2, 1, 1)

        self.but_check_server.clicked.connect(partial(self.checkServer))

        self.but_clear_cache = QPushButton("Clear Cache(potentially large!)")
        self.but_clear_cache.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_main.addWidget(self.but_clear_cache, 0, db.ncol - 1, 1, 1)
        self.but_clear_cache.clicked.connect(partial(self.cs.delete_all_log))

        #########################################
        # buttons for checked servers
        #########################################

        self.cb_all_flx = QCheckBox("All felix")
        self.cb_all_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_flx, 0, 0, 1, 1)

        self.but_init_all_selected_flx = QPushButton("Init checked flx")
        self.but_init_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_init_all_selected_flx, 0, 1, 1, 1)
        self.but_init_all_selected_flx.clicked.connect(partial(self.loop_checked_servers, "flx", "init"))

        self.but_start_all_selected_flx = QPushButton("Start checked servers")
        self.but_start_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_flx, 0, 2, 1, 1)
        self.but_start_all_selected_flx.clicked.connect(partial(self.loop_checked_servers, "flx", "run"))

        self.but_stop_all_selected_flx = QPushButton("Stop checked servers")
        self.but_stop_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_stop_all_selected_flx, 0, 3, 1, 1)
        self.but_stop_all_selected_flx.clicked.connect(partial(self.loop_checked_servers, "flx", "stop"))

        self.but_check_all_selected_flx = QPushButton("Check felix link")
        self.but_check_all_selected_flx.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_check_all_selected_flx, 0, 4, 1, 1)

        self.cb_all_opc = QCheckBox("All opc")
        self.cb_all_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.cb_all_opc, 0, db.ncolflx, 1, 1)

        self.but_start_all_selected_opc = QPushButton("Start checked opc")
        self.but_start_all_selected_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_start_all_selected_opc, 0, db.ncolflx + 1, 1, 1)
        self.but_start_all_selected_opc.clicked.connect(partial(self.loop_checked_servers, "opc", "run"))

        self.but_stop_all_selected_opc = QPushButton("Stop checked opc")
        self.but_stop_all_selected_opc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout_but.addWidget(self.but_stop_all_selected_opc, 0, db.ncolflx + 2, 1, 1)
        self.but_stop_all_selected_opc.clicked.connect(partial(self.loop_checked_servers, "opc", "stop"))



        class Worker(QtCore.QObject):
            finished = QtCore.pyqtSignal()
            def __init__(self, server):
                super().__init__()
                self.server = server
            def run(self):
                self.server.check_and_hold()

        #########################################
        # individual buttons
        #########################################
        nrow = 1
        for flx, server in self.return_list_flx().items():
            server.cs = self.cs
            # TODO: do things based on catching
            server.serverStatus.connect(partial(self.update_server_status))
            server.monitor()

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
            but.clicked.connect(partial(self.init_modified, server))
            server.init_ind = but
            server.init_controller = but

            # this button is for running server(individually)
            but = QPushButton("run server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_run_but[flx] =  but 
            self.layout_but.addWidget(self.l_flx_run_but[flx], nrow, 2, rowspan, 1)
            but.clicked.connect(partial(server.run), QtCore.Qt.UniqueConnection | QtCore.Qt.QueuedConnection)
            server.run_controller = but

            # this button is for running server(individually)
            but = QPushButton("stop server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_stp_but[flx] =  but 
            self.layout_but.addWidget(self.l_flx_stp_but[flx], nrow, 3, rowspan, 1)
            but.clicked.connect(partial(server.stop))
            server.stop_controller = but

            # this button is for checking log(individually)
            but = QPushButton("check log")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_flx_log_but[flx] =  but 
            self.layout_but.addWidget(self.l_flx_log_but[flx], nrow, 4, rowspan, 1)
            but.clicked.connect(partial(server.log, self.parent))
            server.run_ind = but

            nrow += rowspan
            pass # flx

        nrow = 1
        for sector, server in self.return_list_opc().items():
            #  server.set_commands(self.det, sector)
            server.serverStatus.connect(partial(self.update_server_status))
            server.cs = self.cs
            server.monitor()

            #  self.l_thread[sector] = QtCore.QThread() 
            #  self.l_worker[sector] = Worker(server) 
            #  self.l_worker[sector].moveToThread(self.l_thread[sector])
            #  # working and blocking       
            #  self.l_thread[sector].started.connect(server.check_and_hold)
            #  self.l_worker[sector].finished.connect(self.l_thread[sector].quit)
            #  self.l_worker[sector].finished.connect(self.l_worker[sector].deleteLater)
            #  self.l_thread[sector].finished.connect(self.l_thread[sector].deleteLater)
            #  self.l_thread[sector].start()

            rowspan = len(server.l_flx)

            cb = QCheckBox("Opc " + sector)
            cb.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_cb[sector] = cb 
            self.layout_but.addWidget( self.l_opc_cb[sector], nrow, db.ncolflx, rowspan, 1)
            server.checkbox = cb

            but = QPushButton("run server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_run_but[sector] = but 
            self.layout_but.addWidget( self.l_opc_run_but[sector], nrow, db.ncolflx + 1, rowspan, 1)
            but.clicked.connect(partial(server.run))
            server.init_ind = but
            server.run_controller = but

            but = QPushButton("stop server")
            but.setEnabled(False)
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_stp_but[sector] =  but 
            self.layout_but.addWidget( self.l_opc_stp_but[sector], nrow, db.ncolflx + 2, rowspan, 1)
            but.clicked.connect(partial(server.stop))
            server.stop_controller = but

            but = QPushButton("check log")
            but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            self.l_opc_log_but[sector] =  but 
            self.layout_but.addWidget( self.l_opc_log_but[sector], nrow, db.ncolflx + 3, rowspan, 1)
            but.clicked.connect(partial(server.log, self.parent))
            server.run_ind = but

            nrow += rowspan
            pass # opc

        self.set_cb_relationship()
        self.checkServer(True)
        pass

    @QtCore.pyqtSlot()
    def checkServer(self, quiet = False):
        for server in self.return_list_opc().values(): 
            server.check(quiet)
        for server in self.return_list_flx().values(): 
            server.check(quiet)
            pass
        pass

    def set_cb_relationship(self,):
        @QtCore.pyqtSlot(int)
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
            if state == QtCore.Qt.Checked: return
            for cb in l_cb:
                cb.setCheckState(state)
            pass
        for name, cb in self.l_flx_cb.items():
            l_cb_opc_tmp = []
            for opc in self.l_flx[name].l_opc:
                l_cb_opc_tmp.append(self.l_opc_cb[opc])
            cb.stateChanged.connect(partial(toggle_opc_checkbox, name, l_cb_opc_tmp))

        @QtCore.pyqtSlot(int)
        def toggle_flx_checkbox(opc, l_cb, state):
            """
            act upon opc checkbox
            if opc is 2(on), turn on felix, too
            """
            self.l_opc[opc].set_enable_state()
            if state == QtCore.Qt.Unchecked: return
            for cb in l_cb:
                cb.setCheckState(state)
        for name, cb in self.l_opc_cb.items():
            l_flx_cb_tmp = []
            for flx in self.l_opc[name].l_flx:
                l_flx_cb_tmp.append(self.l_flx_cb[flx])
            cb.stateChanged.connect(partial(toggle_flx_checkbox, name, l_flx_cb_tmp))

    @QtCore.pyqtSlot(int)
    def update_server_status(self, status):
        server = self.sender()
        jobname = server.run_jobname
        if status == 0:
            self.s_server_stable.discard(jobname)
            self.s_server_communicating.discard(jobname)
            self.s_server_fatal.discard(jobname)
            pass
        elif status == 1:
            self.s_server_stable.add(jobname)
            self.s_server_communicating.discard(jobname)
            self.s_server_fatal.discard(jobname)
            pass
        elif status == 2:
            self.s_server_stable.discard(jobname)
            self.s_server_communicating.add(jobname)
            self.s_server_fatal.discard(jobname)
            pass
        elif status == 3:
            self.s_server_stable.discard(jobname)
            self.s_server_communicating.discard(jobname)
            self.s_server_fatal.add(jobname)
            pass
        if len(self.s_server_fatal) > 0 :
            self.serverStatus.emit(3)
        elif len(self.s_server_communicating) > 0 :
            self.serverStatus.emit(2)
        elif len(self.s_server_stable) > 0 :
            self.serverStatus.emit(1)
        else:
            self.serverStatus.emit(0)
        pass

    @QtCore.pyqtSlot()
    def check_gbtx(self):
        marker = f"{self.det}-{self.sside}"
        if self.det == "TP":
            marker = "TP"
        self._widLogGBTx = LogChecker(f"GBTx Alignment Checker {marker}", self)
        self._gbtxCounter = 0
        for name, cb in self.l_flx_cb.items():
            if not cb.isChecked(): continue
            self._gbtxCounter += 1
            host = self.return_list_flx()[name].hostname
            @QtCore.pyqtSlot(str)
            def stop_job(host, *args):
                self._gbtxCounter -= 1
                pass


            self.cs.send_command(f"gbt_check_{host}",
                    f"gbt_check_{host}",
                    host,
                    f"{db.FLX_SETUP} && flx-info gbt && flx-info gbt -c1",
                    partial(stop_job, host))
            pass

        def check_finished(timer):
            if self._gbtxCounter > 0:
                pass
            else:
                timer.stop()
                if not self._widLogGBTx: return
                for name, cb in self.l_flx_cb.items():
                    if not cb.isChecked(): continue
                    host = self.return_list_flx()[name].hostname

                    #  print(details, output)
                    sector_str = []
                    if self.det != "TP":
                        for device in range(4):
                            details = {
                                "mode":"device",
                                "host":host.split(".")[0],
                                "deviceNumber":device,
                                "detector":"mm",
                                }
                            if self.det == "sTGC":
                                details["detector"] = "stgc"
                            output = nsw_this.deviceTable(details)
                            sector_l = []
                            for outDic in output:
                                sector_l.append( outDic["sector"] )
                                pass
                            sector_str.append( ",".join(sector_l) )
                    elif "tp-a" in host:
                        sector_str += [
                                "STG A9-A16",
                                "STG A1-A8",
                                "MMG A9-A16",
                                "MMG A1-A8",
                                ]
                    elif "tp-c" in host:
                        sector_str += [
                                "STG C9-C16",
                                "STG C1-C8",
                                "MMG C9-C16",
                                "MMG C1-C8",
                                ]
                    linkMap = [
                            {
                                0:" [A10]",
                                1:" [A12]",
                                4:" [A14]",
                                5:" [A16]",
                                6:" [A9]",
                                7:" [A11]",
                                10:"[A13]",
                                11:"[A15]",
                                },
                            {
                                12:"[A2]",
                                13:"[A4]",
                                16:"[A6]",
                                17:"[A8]",
                                18:"[A1]",
                                19:"[A3]",
                                22:"[A5]",
                                23:"[A7]",
                                },
                            ]
                    if "tp-c" in host:
                        for dic in linkMap:
                            for key, sec in dic.items():
                                dic[key] = sec.replace("A", "C")

                    self._widLogGBTx.textLog.append(f"Host is: {host}\n")
                    fileLog = QtCore.QFile(str(self.cs.full_log(f"gbt_check_{host}")))
                    fileLog.open(QtCore.QIODevice.ReadOnly)
                    if not fileLog.isOpen():
                        continue
                    found = 0
                    while not fileLog.atEnd(): 
                        line = fileLog.readLine()
                        line = codecs.decode(line, "utf-8").strip()
                        if "" == line: continue
                        if "card type" in line.lower(): continue
                        if "firmw type" in line.lower(): continue
                        if "connection to " in line.lower(): continue
                        device = found * 2 - 2
                        if "channel | 12" in line.lower(): 
                            device += 1
                        if "------" in line.lower(): continue
                        if "link alignment status" in line.lower(): 
                            found += 1
                            self._widLogGBTx.textLog.insertPlainText(f"Link alignment status for card: {found-1}"\
                                    f" (device {found * 2 - 2}[{sector_str[found * 2 - 2]}], {found * 2 - 1}[{sector_str[found * 2 - 1]}])\n")
                            continue
                        if found == 0: continue
                        line = line.replace("NO",  "N")
                        line = line.replace("YES", "Y")
                        if "channel" in line.lower() or "aligned" in line.lower():
                            for w in line.split():
                                if "channel" in w.lower() or "aligned" in w.lower(): 
                                    self._widLogGBTx.textLog.insertPlainText("{0: <8}".format(w))
                                elif "|" in w:
                                    self._widLogGBTx.textLog.insertPlainText(w)
                                elif "Y" in w:
                                    self._widLogGBTx.textLog.setTextColor(QtCore.Qt.green)
                                    self._widLogGBTx.textLog.insertPlainText("{0: <11}".format(w))
                                    self._widLogGBTx.textLog.setTextColor(QtCore.Qt.black)
                                elif "Err" in w:
                                    self._widLogGBTx.textLog.setTextColor(QtCore.Qt.red)
                                    self._widLogGBTx.textLog.insertPlainText("{0: <11}".format(w))
                                    self._widLogGBTx.textLog.setTextColor(QtCore.Qt.black)
                                else:
                                    if self.det == "TP" and "channel" in line.lower() and int(w) in linkMap[device % 2]:
                                        w += f"{linkMap[device % 2][int(w)]}"
                                        pass
                                    self._widLogGBTx.textLog.insertPlainText("{0: <11}".format(w))
                            self._widLogGBTx.textLog.insertPlainText("\n")
                        else:
                            self._widLogGBTx.textLog.append(line)
                        pass
                    pass
                self._widLogGBTx.textLog.insertPlainText("\n")
                pass
        timer = QtCore.QTimer()
        timer.start(50)
        timer.timeout.connect(partial(check_finished, timer))
        pass

    # Loop over checked servers and perform the task for each
    def loop_checked_servers(self, server_type = None, task=None):
        if server_type == "flx":
            for (server_name, check_box) in self.l_flx_cb.items():
                if not check_box.checkState(): continue
                server_obj = self.return_list_flx()[server_name]
                if task == "init":
                    self.init_modified(server_obj)
                elif task == "run":
                    server_obj.run()
                elif task == "stop":
                    server_obj.stop()
                else:
                    pass
                pass
            pass
        elif server_type == "opc":
            for (server_name, check_box) in self.l_opc_cb.items():
                if not check_box.checkState(): continue
                server_obj = self.return_list_opc()[server_name]
                if task == "run":
                    server_obj.run()
                elif task == "stop":
                    server_obj.stop()
                else:
                    pass
                pass
            pass
        else:
            pass
        return None

    def init_modified(self, server):
        server.init_command = f"{server.original_init_command} && {self.flx_init_type_list[self.flx_init_type.currentIndex()]}"
        server.init()

    def quit(self):
        # let supervisord run in the background 
        #  self.cs.stop_all()
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
