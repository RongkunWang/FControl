import os, pathlib
from functools import partial
import codecs

from PyQt5.QtCore import pyqtSlot, Qt, QUrl
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QMessageBox

import utilities

class Server(QWidget):
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

        self._cs = None
        self._init_jobname = None
        self._run_jobname = None
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
        # yellow green
        utilities.set_button_color(self.init_ind, QtGui.QColor(173, 255, 47))
        #  utilities.set_palette_color(self.init_ind, QtGui.QPalette.ButtonText, QtGui.QColor(Qt.black))
        pass

    def check(self, ):
        check_job_name = f"check_{self.run_jobname}"
        job = self.cs.send_command(check_job_name, check_job_name,
                self.hostname, self.check_running_command, toFile = False)
        # make asynchronous??
        job.waitForFinished(10000)
        data = codecs.decode(job.readAllStandardOutput(), "utf-8").split("\n")
        return data

    def kill(self, ):
        kill_job_name = f"kill_{self.run_jobname}"
        job = self.cs.send_command(kill_job_name, kill_job_name, 
                self.hostname, f"{self.kill_command} && echo $? && sleep 0.1", toFile = False)
        job.waitForFinished(10000)
        data = codecs.decode(job.readAllStandardOutput(), "utf-8").split("\n")
        return bool(data[0])

    def check_and_kill(self):
        data = self.check()
        user = data[0].split()[0]
        if len(data) > 2:
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


    @pyqtSlot()
    def run(self):
        if not self.check_and_kill():
            return


        @pyqtSlot()
        def stop_job(*args):
            self.set_enable_state()
            pass
        self.cs.send_command(self.run_jobname, 
                self.run_jobname, 
                self.hostname, self.run_command,
                partial(stop_job))
        utilities.set_button_color(self.run_ind, Qt.yellow)
        self.set_enable_state()
        pass

    @pyqtSlot()
    def stop(self):
        if self.cs.has_job(self.run_jobname):
            self.cs.stop_command(self.run_jobname)
        else:
            self.set_enable_state()

        utilities.set_button_color(
                self.run_ind,)
        pass

    @pyqtSlot()
    def log(self):
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
        QtGui.QDesktopServices.openUrl(QUrl.fromLocalFile( str(full_log) ))
        pass

    def health_size(self, full_log):
        # TODO-1: check by checking file size every 3 second
        pass

    def health_message(self):
        "FelixCore Up and Running"
        pass
