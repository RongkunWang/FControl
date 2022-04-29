import os, pathlib, time
from functools import partial
import codecs
from enum import Enum
import signal

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QUrl, QIODevice, QFile, QTimer, QThread, QObject
from PyQt5.QtWidgets import QWidget, QMessageBox

import utilities, db
from LogChecker import LogChecker

class ServerState(Enum):
    NotRunning = 0
    Stable = 1
    Communicating = 2
    Error = 3

class Server(QWidget):
    # stopped 0
    # stable 1
    # communicating 2
    # fatal 3
    serverStatus = pyqtSignal(int)
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
        self._original_init_command = init_server_command
        self._run_command = run_server_command
        self._original_run_command = run_server_command
        self._check_running_command = check_running_command
        self._kill_command = kill_cmd


        self._check_hold_command = "true"

        self.last_cmd = "run"
        #  self.log_name = self.run_jobname

        self.l_window = []
        # 0 not running 1 ready 2 communicating 3 error
        self._state = ServerState.NotRunning

        # signature for actively stopping job
        self.active_stop = False

        # ms
        self._server_timeout      = 5000
        self._server_check_period = 1

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

    def __str__(self):
        return f"Host: {self.hostname}, Job: {self.run_jobname}"

    @property
    def command_name(self):
        return self._command_name

    @property
    def hostname(self):
        return self._hostname

    @property
    def original_init_command(self):
        return self._original_init_command
    @property
    def init_command(self):
        return self._init_command
    @init_command.setter
    def init_command(self, name):
        self._init_command = name

    @property
    def check_hold_command(self):
        return self._check_hold_command
    @check_hold_command.setter
    def check_hold_command(self, name):
        self._check_hold_command = name


    @property
    def original_run_command(self):
        return self._original_run_command
    @property
    def run_command(self):
        return self._run_command
    @run_command.setter
    def run_command(self, name):
        self._run_command = name

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

    # supervisord utility return a string to do while loop checking and keep 
    def check_state(self, cmd, state, filter = ""):
        return f"""supervisorctl status {cmd} | grep "{state}" | grep "{filter}" """

    #  def all_not(self, cmd, state, filter = ""):
        #  # if all of the server not in state, quit
        #  return f"""{self.check_state(cmd, state, filter)}"""

    def hang_until_all_not(self, cmd, state, filter = ""):
        # if all of the server not in state, quit
        return f"""while true; do  sleep 1; out=`{self.check_state(cmd, state, filter)}`; if [[ $out == "" ]]; then break; fi; done """

    def hang_until_one_not(self, cmd, state, filter = ""):
        # if any of the server is not in state, quit
        return f"""while true; do  sleep 1; n1=`supervisorctl status {cmd} | grep "{filter}" | wc -l`; n2=`supervisorctl status {cmd} | grep "{state}" | grep "{filter}" | wc -l`;  if [[ $n1 != $n2 ]]; then supervisorctl status {cmd} | grep "{state}" | grep "{filter}"; break; fi; done """

    # functionality
    def set_enable_state(self, force_disable = False):
        if force_disable or not self.checkbox.isChecked() or \
                (self.init_jobname and self.cs.has_job(self.init_jobname)):
            if self.init_controller:
                self.init_controller.setEnabled(False)
            self.run_controller.setEnabled(False)
            self.stop_controller.setEnabled(False)
        else:
            if self.init_controller:
                self.init_controller.setEnabled(True)
            self.run_controller.setEnabled(True)
            self.stop_controller.setEnabled(True)
        pass
    
    @pyqtSlot()
    def init(self):
        #  if not self.check_and_kill():
            #  return
        @pyqtSlot()
        def stop_job(*args):
            utilities.set_button_color(self.init_ind)
            self.set_enable_state()
            #  self.NotRunning()
            self.serverStatus.emit(0)
        self.last_cmd = "init"
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
                self.hostname, self.check_running_command, toFile = False, quiet = True, thread = self.thread)
        # TODO: make asynchronous??
        #  job.waitForFinished(self._server_timeout)
        def analyze(job):
            if not job:
                self._runTimer.start()
                return
            data = codecs.decode(job.readAllStandardOutput(), "utf-8").split("\n")
            data = self.strip(data)
            if len(data) == 0:
                self.stopped()
                pass
            else: 
                if db.DEBUG:
                    print(self.hostname, data)
                s = self.cs.check_size(self.run_jobname)
                if self._logSize == s and "STARTING" not in data:
                    self.stable()
                else:
                    self.communicating()
                self._logSize = s
            self._runTimer.start()
        job.finished.connect(partial(analyze, job))

    def strip(self, data):
        host_key_changed = False
        index = 0
        last = -1
        for i, var in enumerate(data):
            if "@@@@@@@@@@@" in var and i == 0:
                #  print("@@@ found")
                host_key_changed = True
                continue

            if "ECDSA key" in var:
                host_key_changed = True
                continue

            #  if "Connection to" in var and "closed" in var:
                #  continue

            if "bashrc" in var:
                continue

            if f"Connection to {self.hostname} closed." in var:
                last = i
                break

            if (host_key_changed) and ("X11 forwarding is disabled" in var):
                #  print("middle")
                index = i+1
                break

            if "Warning: Permanently added" in var:
                index = i+1
                break

            if "Killed by signal 2" in var:
                last = i
                break

            if "xauth" in var:
                index = i+1
                continue
            if "Setting up FELIX" in var:
                index = i+1
                continue
            if "Did not find" in var:
                index = i+1
                continue
            if "Using" in var:
                index = i+1
                continue
            pass
        return data[index:last]

    def kill(self, ):
        kill_job_name = f"kill_{self.run_jobname}"
        job = self.cs.send_command(kill_job_name, kill_job_name, 
                self.hostname, f"{self.kill_command} && echo $? && sleep 0.1", toFile = True)
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
            self.serverStatus.emit(2)
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
            self.serverStatus.emit(1)
            self._state = ServerState.Stable

    def stopped(self):
        """
        state indicator
        """
        utilities.set_button_color(self.run_ind)
        if self._state != ServerState.NotRunning:
            self.serverStatus.emit(0)
            self._state = ServerState.NotRunning

    @pyqtSlot()
    def run(self):
        #  if not self.check_and_kill():
            #  return
        if self.cs.has_job(self.run_jobname):
            self.active_stop = True
            self.cs.stop_command(self.run_jobname)
            self.active_stop = False

        # already has text log, meaning the log window is opened
        if self._textLog:
            self._textLog.clear()
            if self._fileLog and self._fileLog.isOpen():
                self._fileLog.close()
                self._fileLog = None
            pass

        @pyqtSlot()
        def stop_job(*args):
            #  self.kill()
            #  self.serverStatus.emit(0)
            #  self.set_enable_state()
            #  utilities.set_button_color(self.run_ind)
            #  self.monitor(False)
            #  if not self.active_stop:
                #  QMessageBox.warning(self, "Server killed", 
                        #  f"Please make sure supervisord is running. \nOr there's something wrong with the config(contact {db.author} if you suspect it's the case).")
            pass
        self.last_cmd = "run"
        self.cs.send_command(self.run_jobname, 
                self.run_jobname, 
                self.hostname, self.run_command,
                partial(stop_job))
        #  self._fileMon = QFile(str(self.cs.full_log(self.run_jobname)))
        #  self._fileMon.open(QIODevice.ReadOnly)

        #  self.set_enable_state()
        #  self.monitor()

        pass

    @pyqtSlot()
    def stop(self):
        """
        triggered by stop button
        """
        self.active_stop = True
        self.cs.stop_command(self.run_jobname)
        state = self.kill()
        self.active_stop = False
        pass


    def update_log(self, wid, text):
        pass

    @pyqtSlot()
    def log(self, parent):
        if self._textLog:
            getattr(self._textLog.parentWidget(), "raise")()
            return
        # TODO: Qt console
        self.log_name = self.run_jobname
        if self.last_cmd == "init":
            self.log_name = self.init_jobname
        full_log = self.cs.full_log(self.log_name)

        if not self.cs.has_job(self.log_name):
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
        wid = LogChecker(self.log_name)
        self._textLog = wid.textLog

        if self._fileLog:
            self._fileLog.close()

        # do it first before the timeout ends
        self.read()

        # TODO: two timer good or bad?
        self._readTimer.start(self._server_check_period)
        self._readTimer.timeout.connect(partial(self.read))

        # TODO:urgent re-enable the window
        wid.closed.connect(partial(self.stop_read))
        self._widLog = wid
        pass

    @pyqtSlot()
    def stop_read(self):
        # TODO: do I need to close it??
        if self._fileLog:
            self._readTimer.stop()
            self._fileLog.close()
            self._fileLog = None
            self._textLog = None
            try:
                self._readTimer.timeout.disconnect()
            except TypeError:
                print("exception when disconnect, continue")

    def monitor(self):
        """
        monitor server status
        """
        class Worker(QObject):
            finished = pyqtSignal()
            def __init__(self, server):
                super().__init__()
                self.server = server
            def run(self):
                data = self.server.check()
                if len(data) <= 2:
                    print("stopping")
                    self.server.stopped()
                    pass
                else: 
                    print("running?")
                    s = self.server.cs.check_size(self.server.run_jobname)
                    if self.server._logSize == s and "STARTING" not in data:
                        self.server.stable()
                    else:
                        self.server.communicating()
                    self.server._logSize = s
                self.finished.emit()

        def check_run():
            #  self.check()
            if len(data) <= 2:
                self.stopped()
                pass
            else: 
                #  self._logSize = -1
                s = self.cs.check_size(self.run_jobname)
                if self._logSize == s:
                    self.stable()
                else:
                    self.communicating()
                self._logSize = s
            #  self.thread = QThread()
            #  self.worker = Worker(self)
            #  self.worker.moveToThread(self.thread)
            #  self.thread.started.connect(self.worker.run)
            #  self.worker.finished.connect(self.thread.quit)
            #  self.thread.finished.connect(self.thread.deleteLater)
            #  self.worker.finished.connect(self.worker.deleteLater)
            #  self.thread.start()

        #  class WorkingThread(QThread):
            #  def __init__(self, server):
                #  super().__init__()
                #  self.server = server
                #  self.moveToThread(self)
                #  #  pass
            #  def run(self, ):
                #  timer = QTimer(self)
                #  timer.setInterval(self.server._server_check_period)
                #  timer.timeout.connect(partial(check_run))
                #  timer.start()
                #  pass


        #  self._runTimer.timeout
        #  self.thread = WorkingThread(self)
        #  self.thread = QThread()
        self._runTimer.setInterval(self._server_check_period)
        self._runTimer.setSingleShot(True)
        self._runTimer.timeout.connect(partial(self.check))
        self._runTimer.start()
        #  self._runTimer.moveToThread(self.thread)
        #  self.thread.started.connect(self._runTimer.start)
        #  self.thread.start()
        #  self._runTimer.start(self._server_check_period)

        #  if start == True:
            #  self._logSize = -1
            #  self._runTimer.start(self._server_check_period)
            #  def check_size():
                #  s = self.cs.check_size(self.run_jobname)
                #  if self._logSize == s:
                    #  self.stable()
                #  else:
                    #  self.communicating()
                #  self._logSize = s
            #  self._runTimer.timeout.connect(partial(check_size))
        #  else:
            #  self._runTimer.stop()
            #  self._runTimer.timeout.disconnect()
            #  pass

    @pyqtSlot()
    def read(self):
        def handler(signum, frame):
            raise Exception("End of time")
            pass
        signal.signal(signal.SIGALRM, handler)

        signal.alarm(10)
        try:
            self.read_noTimeout()
        except Exception as exc:
            msgBox = QMessageBox.critical(self, f"{exc}",
                    "Timeout after 10 seconds. stop log reading. Please check if the corresponding log is too large!")
            self.stop_read()

        # cancel the alarm
        signal.alarm(0)
        pass

    def read_noTimeout(self):
        """
        asynchronous reading
        #  """

        if not self._fileLog:
            #  if not self._fileLog:
            self._fileLog = QFile(str(self.cs.full_log(self.log_name)))
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
                pass
            pass
        pass

