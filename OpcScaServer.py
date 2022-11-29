import db
from Server import Server

class OpcScaServer(Server):
    def __init__(self, flx_host, port):
        first_check_running = self.check_state(f"{db.OPC_EXE}:opcserver-{port} {flx_host}", 
                "RUNNING\|STARTING", f"{db.OPC_EXE}:opcserver-{port}")
        Server.__init__(self, 
                flx_host, 
                f"{db.OPC_EXE}", 
                "true", # init server
                f"""{db.FLX_SETUP} && echo "Yes" | felix-multivisor "start {db.OPC_EXE}:opcserver-{port}" {flx_host}""", # run server
                f"""{db.FLX_SETUP} && {first_check_running}""", # check
                f"""{db.FLX_SETUP} && echo "Yes" | felix-multivisor "stop {db.OPC_EXE}:opcserver-{port}" {flx_host}""", # kill server
                is_multivisor = True,
                )
        self._l_flx = []
        self.host = flx_host

        # TODO use case unclear
        #  hang_running = self.hang_until_all_not(f"{db.OPC_EXE}:opcserver-{port}", "RUNNING\|STARTING")
        #  self.check_hold_command = f"""{db.FLX_SETUP} && {hang_running}"""
        pass

    def set_commands(self, det, sector):
        """
        seems unused now
        """

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
    pass
