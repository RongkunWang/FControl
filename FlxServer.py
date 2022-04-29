from PyQt5 import QtGui

import db
from Server import Server

class FlxServer(Server):
    def __init__(self, flx_host):
        # check also TPCtrlPanel.py
        cmd = f"{db.FLX_SETUP}"
        #  cmd = f"{db.FLX_SETUP} && flx-init && echo && flx-init -c1"
        # for sector ones
        if flx_host not in (db.flx_dict["TP"]["A"] + db.flx_dict["TP"]["C"]):
            cmd = f"{db.FLX_SETUP} && /det/nsw/felix-configuration/nsw_felix_config.sh -n && echo && /atlas-home/0/ptzanis/Documents/conf_l1ddc.sh"
            pass
        Server.__init__(self, 
                flx_host,
                f"{db.FLX_EXE}",
                cmd,
                f"{db.FLX_SETUP} && {db.FLX_EXE} {db.flx_arg[flx_host]}",
                f"""ps aux | grep '{db.FLX_EXE}\|felix-tohost\|felix-toflx' | grep -v 'bash\|grep' """,
                f"{db.FLX_SETUP} && supervisorctl stop all; killall -9 {db.FLX_EXE}",
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

    def health_message(self):
        # TODO add healthy and unhealth messages?!
        """
        message that appears 
        """

        self.health_word = 1
        "FelixCore Up and Running"
        pass

    pass
