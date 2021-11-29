import db
from Server import Server

class FlxServer(Server):
    def __init__(self, flx_host):
        Server.__init__(self, flx_host,
                f"{db.FLX_EXE}",
                f"{db.FLX_SETUP} && flx-init && echo && flx-init -c1",
                f"{db.FLX_SETUP} && {db.FLX_EXE} {db.flx_arg[flx_host]}",
                f"ps aux | grep {db.FLX_EXE} | grep -v grep",
                f"killall -9 {db.FLX_EXE}",
                )
        self._l_opc = set()
        self.init_jobname = f"init_{flx_host}"
        self.run_jobname = f"felixcore_{flx_host}"
        pass

    @property
    def l_opc(self):
        return self._l_opc

    @l_opc.setter
    def l_opc(self, opcs):
        self._l_opc = opcs

    pass
