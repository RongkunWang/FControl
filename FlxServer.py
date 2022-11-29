from PyQt5 import QtGui

import db
from Server import Server

class FlxServer(Server):
    def __init__(self, flx_host):
        # check also TPCtrlPanel.py
        init_cmd = f"""{db.FLX_SETUP} && echo "Yes" | felix-multivisor "start 20_init_blocking:*" {flx_host} """

        """
        will stop running state once any of the process stops
        """
        first_check_running = self.check_state(f"{db.FLX_EXE}:* {flx_host}", "RUNNING\|STARTING", "register\|toflx\|tohost\|felix2atlas")

        Server.__init__(self, 
                flx_host,
                f"{db.FLX_EXE}", 
                init_cmd, # init server
                f"""{db.FLX_SETUP} && echo "Yes" | felix-multivisor "start {db.FLX_EXE}:*" {flx_host} """, # run server
                f"""{db.FLX_SETUP} && {first_check_running}""", # check
                f"""{db.FLX_SETUP} && echo "Yes" | felix-multivisor "stop {db.FLX_EXE}:*"  {flx_host} """, # kill
                is_multivisor = True,
                )
        self._l_opc = set()
        self.host = flx_host
        self.init_jobname = f"init_{flx_host}"
        self.run_jobname = f"felixstar_{flx_host}"

        # TODO use case unclear
        #  hang_running = self.hang_until_all_not(f"{db.FLX_EXE}:*", "RUNNING\|STARTING", "register\|toflx\|tohost\|felix2atlas")
        #  self.check_hold_command = f"""{db.FLX_SETUP} && {hang_running}"""
        
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
