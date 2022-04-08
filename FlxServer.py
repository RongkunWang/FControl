from PyQt5 import QtGui

import db
from Server import Server

class FlxServer(Server):
    def __init__(self, flx_host):
        # check also TPCtrlPanel.py
        cmd = f"{db.FLX_SETUP}"
        # REMOVE  for sector ones
        #  if flx_host not in (db.flx_dict["TP"]["A"] + db.flx_dict["TP"]["C"]):
        hang_init = self.hang_until_all_not("20_init_blocking:*", "RUNNING\|STARTING")
        cmd = f"""{db.FLX_SETUP} && supervisorctl start 20_init_blocking:* && {hang_init}"""

        """
        will stop running state once any of the process stops
        """
        hang_running = self.hang_until_all_not(f"{db.FLX_EXE}:*", "RUNNING\|STARTING", "register\|toflx\|tohost\|felix2atlas")
        first_check_running = self.check_state(f"{db.FLX_EXE}:*", "RUNNING\|STARTING", "register\|toflx\|tohost\|felix2atlas")

        Server.__init__(self, 
                flx_host,
                f"{db.FLX_EXE}", 
                cmd, # init server
                f"""{db.FLX_SETUP} && supervisorctl start {db.FLX_EXE}:* """, # run server
                f"""{db.FLX_SETUP} && {first_check_running}""", # check
                f"{db.FLX_SETUP} && supervisorctl stop {db.FLX_EXE}:* ", # kill
                )
        self._l_opc = set()
        self.init_jobname = f"init_{flx_host}"
        self.run_jobname = f"felixcore_{flx_host}"

        self.check_hold_command = f"""{db.FLX_SETUP} && {hang_running}"""
        
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
