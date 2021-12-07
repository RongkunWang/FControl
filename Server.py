import os, pathlib, time
from functools import partial
import codecs
from enum import Enum

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QUrl, QIODevice, QFile, QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDialog, QMessageBox, QTextBrowser

import utilities, db

class ServerState(Enum):
    NotRunning = 0
    Stable = 1
    Communicating = 2
    Error = 3

class Server(QWidget):
    class LogChecker(QWidget):
        closed = pyqtSignal()
        def __init__(self):
            super(Server.LogChecker, self).__init__()

        def closeEvent(self, event): 
            self.closed.emit()
            pass
        pass

    stableSignal = pyqtSignal()
    communicatingSignal = pyqtSignal()
    def __init__(self, 
            hostname, 
            command_name,
            init_server_command,
            run_server_command,
            check_running_command,
            kill_cmd
            ):

        QWidget.__init__(self)

        """
        should only be called by inherited class
        """
        self._hostname = hostname
        self._command_name = command_name
        self._init_command = init_server_command
        self._run_command = run_server_command
        self._check_running_command = check_running_command
        self._kill_command = kill_cmd

        self.l_window = []
        # 0 not running 1 ready 2 communicating 3 error
        self._state = ServerState.NotRunning

        # signature for actively stopping job
        self.active_stop = False

        # ms
        self._server_timeout      = 5000
        self._server_check_period = 1000

        self._fileLog = None 
        self._logSize = -1
        self._widLog = None
        self._textLog = None

        self._cs = None
        self._init_jobname = None
        self._run_jobname = None
        self._runTimer = QTimer()
        self._readTimer = QTimer()
        self._init_ind = None
        self._run_ind = None
        self._checkbox = None
        self._init_controller = None
        self._run_controller = None
        self._stop_controller = None
        pass

    @property
    def command_name(self):
        return self._command_name

    @property
    def hostname(self):
        return self._hostname

    @property
    def init_command(self):
        return self._init_command

    @property
    def run_command(self):
        return self._run_command

    @property
    def check_running_command(self):
        return self._check_running_command

    @property
    def kill_command(self):
        return self._kill_command

    @property
    def cs(self,):
        return self._cs
    @cs.setter
    def cs(self, name):
        self._cs = name

    @property
    def run_jobname(self,):
        return self._run_jobname
    @run_jobname.setter
    def run_jobname(self, name):
        self._run_jobname = name

    @property
    def init_jobname(self,):
        return self._init_jobname
    @init_jobname.setter
    def init_jobname(self, name):
        self._init_jobname = name

    @property
    def init_ind(self,):
        return self._init_ind
    @init_ind.setter
    def init_ind(self, name):
        self._init_ind = name

    @property
    def run_ind(self,):
        return self._run_ind
    @run_ind.setter
    def run_ind(self, name):
        self._run_ind = name

    @property
    def checkbox(self):
        return self._checkbox
    @checkbox.setter
    def checkbox(self, b):
        self._checkbox = b

    """
    optional!
    """
    @property
    def init_controller(self):
        return self._init_controller
    @init_controller.setter
    def init_controller(self, b):
        self._init_controller = b

    @property
    def run_controller(self):
        return self._run_controller
    @run_controller.setter
    def run_controller(self, b):
        self._run_controller = b

    @property
    def stop_controller(self):
        return self._stop_controller
    @stop_controller.setter
    def stop_controller(self, b):
        self._stop_controller = b


    # functionality
    def set_enable_state(self, force_disable = False):
        if force_disable or not self.checkbox.isChecked() or \
                (self.init_jobname and self.cs.has_job(self.init_jobname)):
            if self.init_controller:
                self.init_controller.setEnabled(False)
            self.run_controller.setEnabled(False)
            self.stop_controller.setEnabled(False)
        else:
            if self.cs.has_job(self.run_jobname):
                if self.init_controller:
                    self.init_controller.setEnabled(False)
                self.run_controller.setEnabled(False)
                self.stop_controller.setEnabled(True)
            else:
                if self.init_controller:
                    self.init_controller.setEnabled(True)
                self.run_controller.setEnabled(True)
                self.stop_controller.setEnabled(False)
        pass
    
    @pyqtSlot()
    def init(self):
        if not self.check_and_kill():
            return
        @pyqtSlot()
        def stop_job(*args):
            utilities.set_button_color(self.init_ind)
            self.set_enable_state()
        self.cs.send_command(self.init_jobname, 
                self.init_jobname, 
                self.hostname,
                self.init_command,
                partial(stop_job))
        self.set_enable_state()
        self.stable(self.init_ind)
        pass

    def check(self, ):
        check_job_name = f"check_{self.run_jobname}"
        job = self.cs.send_command(check_job_name, check_job_name,
                self.hostname, self.check_running_command, toFile = False)
        # TODO: make asynchronous??
        job.waitForFinished(self._server_timeout)
        data = codecs.decode(job.readAllStandardOutput(), "utf-8").split("\n")
        data = self.strip(data)
        print(data)
        return data

    def strip(self, data):
        host_key_changed = False
        index = 0
        for i, var in enumerate(data):
            if "@@@@@@@@@@@" in var and i == 0:
                print("@@@ found")
                host_key_changed = True
                continue
            if (host_key_changed) and ("X11 forwarding is disabled" in var):
                print("middle")
                index = i+1
                break

            if "Warning: Permanently added" in var:
                index = i+1
                break

            pass
        return data[index:]

    def kill(self, ):
        kill_job_name = f"kill_{self.run_jobname}"
        job = self.cs.send_command(kill_job_name, kill_job_name, 
                self.hostname, f"{self.kill_command} && echo $? && sleep 0.1", toFile = False)
        job.waitForFinished(self._server_timeout)
        data = codecs.decode(job.readAllStandardOutput(), "utf-8").split("\n")
        return bool(data[0])

    def check_and_kill(self):
        data = self.check()
        if len(data) == 1 and data[0] == "":
            msgBox = QMessageBox.warning(self, "Is Server On?", 
                f"Please check if PC {self.hostname} is powered on.")
            return False
        if len(data) > 2:
            user = data[0].split()[0]
            ret = QMessageBox.question(self, "Running server",
                    f"Server process {self.command_name} already running on {self.hostname}: \n\n    \"{data[0]}\"\n\n Try killing it?", 
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No)
            if ret == QMessageBox.No: return False
            state = self.kill()
            print(state)
            if not state:
                msgBox = QMessageBox.warning(self, "Not killable server", 
                    f"No permission to kill the existing server. Please kindly ask [{user}] to kill the servers on {self.hostname}.")
                return False
        return True

    def communicating(self):
        """
        state indicator
        """
        utilities.set_button_color(self.run_ind, Qt.yellow)
        if self._state != ServerState.Communicating:
            self.communicatingSignal.emit()
            self._state = ServerState.Communicating

    def stable(self, but = None):
        """
        state indicator
        """
        color = Qt.green
        if not but:
            but = self.run_ind
        utilities.set_button_color(but, color)
        if self._state != ServerState.Stable:
            self.stableSignal.emit()
            self._state = ServerState.Stable



    #  def stop(self, ):
        #  pass


    @pyqtSlot()
    def run(self):
        if not self.check_and_kill():
            return

        # already has text log, meaning the log window is opened
        if self._textLog:
            self._textLog.clear()
            if self._fileLog and self._fileLog.isOpen():
                self._fileLog.close()
                self._fileLog = None
            pass

        @pyqtSlot()
        def stop_job(*args):
            self.set_enable_state()
            utilities.set_button_color(self.run_ind)
            self.monitor(False)
            if not self.active_stop:
                QMessageBox.warning(self, "Server killed", 
                        f"Oops, someone killed your {self.run_jobname}. Or there's something wrong with the config(contact {db.author} if you suspect it's the case).")
            pass
        self.cs.send_command(self.run_jobname, 
                self.run_jobname, 
                self.hostname, self.run_command,
                partial(stop_job))
        #  self._fileMon = QFile(str(self.cs.full_log(self.run_jobname)))
        #  self._fileMon.open(QIODevice.ReadOnly)

        self.set_enable_state()
        self.monitor()

        pass

    @pyqtSlot()
    def stop(self):
        self.active_stop = True
        self.cs.stop_command(self.run_jobname)
        self.active_stop = False
        pass


    def update_log(self, wid, text):
        pass

    @pyqtSlot()
    def log(self, parent):
        if self._textLog:
            return
        # TODO: Qt console
        full_log = self.cs.full_log(self.run_jobname)
        if not self.cs.has_job(self.run_jobname):
            #  not active job
            if full_log.is_file():
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
            pass

        # the easy
        # QtGui.QDesktopServices.openUrl(QUrl.fromLocalFile( str(full_log) ))

        # the better
        wid = Server.LogChecker()
        #  wid = QWidget(parent)
        #  wid = QDialog(parent)
        #  wid = QtGui.QWindow()
        #  wid.setModal(True)
        #  print(wid.isModal())
        wid.resize(1200, 800)
        wid.setWindowTitle(f"log {self.run_jobname}")
        #  wid.setTitle(f"log {self.run_jobname}")

        #  widget = QWidget(wid)

        self._textLog = QTextBrowser(wid)
        lay = QHBoxLayout(wid)
        lay.addWidget(self._textLog)
        wid.show()

        # do it first before the timeout ends
        self.read()

        # TODO: two timer good or bad?
        self._readTimer.start(self._server_check_period)
        self._readTimer.timeout.connect(partial(self.read))

        def stop_read():
            # TODO: do I need to close it??
            if self._fileLog:
                self._readTimer.stop()
                self._fileLog.close()
                self._fileLog = None
                self._textLog = None
                self._readTimer.timeout.disconnect()
        # TODO:urgent re-enable the window
        #  wid.finished.connect(partial(stop_read))
        wid.closed.connect(partial(stop_read))
        self._widLog = wid
        pass


    def monitor(self, start = True):
        """
        start monitor if start=True, else stop
        """

        if start == True:
            self._logSize = -1
            self._runTimer.start(self._server_check_period)
            def check_size():
                s = self.cs.check_size(self.run_jobname)
                if self._logSize == s:
                    self.stable()
                else:
                    self.communicating()
                self._logSize = s
            self._runTimer.timeout.connect(partial(check_size))
        else:
            self._runTimer.stop()
            self._runTimer.timeout.disconnect()
            pass

    @pyqtSlot()
    def read(self):
        """
        asynchronous reading
        #  """
        if not self._fileLog:
            self._fileLog = QFile(str(self.cs.full_log(self.run_jobname)))
            self._fileLog.open(QIODevice.ReadOnly)

        # open device
        if not self._fileLog.isOpen():
            return

        while not self._fileLog.atEnd():
            line = self._fileLog.readLine()
            line = codecs.decode(line, "utf-8").strip()
            if self._textLog:
                self._textLog.append(line)
            else:
                print(line)
                pass
            pass
        pass

