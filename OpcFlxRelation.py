from FlxServer import FlxServer
from OpcScaServer import OpcScaServer

# Abstract
class OpcFlxRelation:
    def __init__(self):
        self.l_flx = {}
        self.l_opc = {}

    def return_list_opc(self):
        return self.l_opc

    def return_list_flx(self,):
        return self.l_flx

    def add_opc_flx(self, opc, l_flx):
        """
        set up how an opc(sector) is relied on an felix.
            the first element is where the opc server will be run

        starting this opc requires felixcore.
            to be run on those corresponding felix
        restarting this opc from scratch will certainly requires restarting those felix as well

        killing the corresponding felix will kill all related opc
        """
        flx = l_flx[0]
        self.l_opc[opc] = OpcScaServer(flx)
        for flx in l_flx:
            if flx not in self.l_flx:
                self.l_flx[flx] = FlxServer(flx)
        self.l_opc[opc].l_flx = list(l_flx)
        for flx in l_flx:
            self.l_flx[flx].l_opc.add(opc)
            pass
        pass

    def kill_chain_flx(self, flx):
        """
        if you kill this felix, you would of course kill those opc
        """
        flx_set = set([flx])
        opc_set = set()
        for opc in self.l_flx[flx].l_opc:
            opc_set.add(opc)
            pass
        return flx_set, opc_set

    def restart_chain_opc(self, opc):
        """
        if you want to restart this opc, you need to restart/kill the felix, and the corresponding opc, too
            (if you just want to kill this opc, simply do it..)
        """
        flx_set = set()
        opc_set = set([opc])
        for flx in self.l_opc[opc].l_flx:
            flx_set.add(flx)
            opc_set.update(self.kill_chain_flx(flx)[1])
            pass
        return flx_set, opc_set

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    q = QApplication(sys.argv)
    a = OpcFlxRelation()
    a.add_opc_flx(1, ["pc-tdq-flx-nsw-mm-01.cern.ch"])
    a.add_opc_flx(2, ["pc-tdq-flx-nsw-mm-01.cern.ch"])
    a.add_opc_flx(3, ["pc-tdq-flx-nsw-mm-01.cern.ch", "pc-tdq-flx-nsw-mm-02.cern.ch"])
    a.add_opc_flx(4, ["pc-tdq-flx-nsw-mm-02.cern.ch"])
    a.add_opc_flx(5, ["pc-tdq-flx-nsw-mm-02.cern.ch"])
    a.add_opc_flx(6, ["pc-tdq-flx-nsw-mm-03.cern.ch", "pc-tdq-flx-nsw-mm-02.cern.ch"])
    a.add_opc_flx(7, ["pc-tdq-flx-nsw-mm-03.cern.ch"])
    a.add_opc_flx(8, ["pc-tdq-flx-nsw-mm-03.cern.ch"])
    print(a.kill_chain_flx("pc-tdq-flx-nsw-mm-01.cern.ch"))
