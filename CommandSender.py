import subprocess, signal
import os, shutil
import pathlib
import time

from PyQt5.QtCore import QProcess, QIODevice
from PyQt5.QtWidgets import QWidget, QMessageBox

USER = os.environ["USER"]

class CommandSender(QWidget, ):
    def __init__(self, log_dir):
        QWidget.__init__(self)

        self.d_running_command = {}
        self.d_log_file = {}
        self.d_log_size = {}
        self.log_dir = pathlib.Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        pass

    def __getitem__(self, key):
        if not self.has_job(key):
            return None
        return self.d_running_command[key]

    def full_log(self, name):
        return self.log_dir / name

    def send_command(self, name, log_file, host, cmd, finish_func = None, state_changed_func = None, toFile = True):
        print("\nstarting command", name, cmd)

        self.d_log_file[name] = self.log_dir / log_file

        #  CMD = f"ssh -o StrictHostKeyChecking=no -t {host} \"stty isig intr ^N -echoctl ; trap '/bin/true' SIGINT; trap '/bin/true' SIGQUIT; {cmd}\""
        CMD = f"ssh -o StrictHostKeyChecking=no -t -t {host} \"{cmd}\""

        # QProcess
        job = QProcess()
        job.setProcessChannelMode( QProcess.MergedChannels ) 
        if toFile:
            job.setStandardOutputFile( str(self.d_log_file[name]), QIODevice.Truncate | QIODevice.ReadWrite )
        #  job.setProgram(CMD)
        #  job.start(QIODevice.ReadWrite)
        job.start(CMD)

        def finish_action(*args):
            self.stop_command(name)
            if finish_func:
                finish_func(*args)
            pass
        job.finished.connect(finish_action)
        def state_change_action(*args):
            if state_changed_func:
                state_changed_func(*args)
                pass
            pass
        job.stateChanged.connect(state_change_action)
        
        self.d_running_command[name] = job
        return job
        pass

    def check_size(self, name):
        s = os.path.getsize(self.d_log_file[name])
        self.d_log_size[name] = s
        return s

    def stop_command(self, name):
        if not self.has_job(name):
            # TODO: this is called twice sometimes..
            return
        print("\nstopping command", name)
        self.d_running_command[name].terminate()

        del self.d_running_command[name]
        pass

    def stop_all(self):
        for job in self.d_running_command.values():
            job.terminate()
        #  for job_name in self.d_running_command:
            #  self.stop_command(job_name)
            pass
        pass

    def has_job(self, name):
        if name in self.d_running_command:
            return True
        return False

    def retrieve_log(self, name): 
        pass

    def delete_all_log(self):
        for f in self.log_dir.iterdir():
            print("Deleting " / f)
            if f.is_file():
                try:
                    f.unlink()
                except OSError:
                    msgBox = QMessageBox.warning(self, "Running server", 
                        f"You have running server, stop them before clearing cache!")
            elif f.is_dir():
                shutil.rmtree(f)
        pass

    pass

if __name__ == "__main__":
    cs = CommandSender(f"/tmp/{USER}/GUIGUI")
    cs.send_command("test", "test_gui", 
            "echo test; watch ls")
