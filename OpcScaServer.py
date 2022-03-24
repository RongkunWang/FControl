import db
from Server import Server

class OpcScaServer(Server):
    def __init__(self, flx_host):
        Server.__init__(self, 
                flx_host, 
                f"{db.OPC_EXE}",
                f"{db.FLX_SETUP}",
                "true",
                "true",
                f"killall -9 {db.OPC_EXE}",
                )
        self._l_flx = []
        pass

    def set_commands(self, det, sector):
        self.run_jobname = f"opc_{sector}"
        self._run_command = f"export PATH={db.OPC_EXE_DIR}:$PATH && "\
                f"{db.OPC_EXE} {db.OpcPortFile(db.port_dict[det][sector])} {db.opc_dict[det][sector]}"
        self._original_run_command = self.run_command
        self._check_running_command = f"ps aux | grep {db.OPC_EXE} | grep {db.opc_dict[det][sector]} | grep -v grep"
        pass

    @property
    def l_flx(self):
        return self._l_flx

    @l_flx.setter
    def l_flx(self, flxs):
        self._l_flx = flxs

    def check(self):
        #  data = super(Server, self).check(self)
        data = super().check()
        if len(data) > 2:
            pid = data[0].split()[1]
            self._kill_command = f"kill -9 {pid}"
        return data
    pass
