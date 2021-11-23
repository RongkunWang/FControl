import subprocess
import os
import pathlib

USER = os.environ["USER"]

class CommandSender:
    def __init__(self, log_dir):
        self.d_running_command = {}
        self.d_log_file = {}
        self.log_dir = log_dir
        pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
        pass

    def send_command(self, name, log_file, cmd):
        self.d_log_file[name] = open(os.path.join(self.log_dir, log_file), "w")
        job = subprocess.Popen(cmd, 
                stdout = self.d_log_file[name], 
                stderr = self.d_log_file[name], 
                bufsize = 1, universal_newlines = True, shell = True)
        self.d_running_command[name] = job
        pass

    def stop_command(self, name):
        self.d_running_command[name].terminate()
        self.d_log_file[name].close()

        del self.d_running_command[name]
        del self.d_log_file[name]
        pass


    def stop_all(self):
        for i in list(self.d_running_command):
            self.stop_command(i)
            pass
        pass

    def has_job(self, name):
        if name in self.d_running_command:
            return True
        return False


    def retrieve_log(self, name): 
        pass
    pass

if __name__ == "__main__":
    cs = CommandSender(f"/tmp/{USER}/GUIGUI")
    cs.send_command("test", "test_gui", 
            "echo test; watch ls")
