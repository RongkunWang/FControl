import subprocess
import os

USER = os.environ["USER"]
class CommandSender:
    def __init__(self):
        self.d_running_command = {}
        self.d_log_file = {}
        pass

    def send_command(self, name, cmd, log_file):
        self.d_log_file[name] = open(log_file, "w")
        job = subprocess.Popen(cmd, 
                stdout = self.d_log_file[name], 
                stderr = self.d_log_file[name], 
                bufsize = 1, universal_newlines = True, shell = True)
        self.d_running_command[name] = job
        pass

    def stop_command(self, name):
        self.d_running_command[name].terminate()
        self.d_log_file[name].close()
        pass

    pass

if __name__ == "__main__":
    cs = CommandSender()
    cs.send_command("test", ["echo test; watch ls"],
            f"/tmp/{USER}/test_gui")
    #  cs.d_running_command["test"].wait()
