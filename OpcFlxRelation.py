# Abstract
class OpcFlxRelation:
    def __init__(self):
        self.d_flx_opc = {}
        self.d_opc_flx = {}
        self.d_opc_port = {}


    def return_list_opc(self):
        la, lc = [], []
        for i in self.d_opc_flx:
            if "A" in i:
                la.append(i)
            if "C" in i:
                lc.append(i)
        return [la, lc]

    def return_list_flx(self,):
        """
        return a list of flx server that is used, ordered in sector order
        """
        l = [set(), set()]
        for sector in sorted(self.d_opc_flx):
            flx = self.d_opc_flx[sector][0]
            if "A" in sector:
                l[0].add(flx)
            if "C" in sector:
                l[1].add(flx)
        return sorted(l[0]), sorted(l[1])

    def opc_flx(self, opc, l_flx, port = 48020):
        """
        set up how an opc(sector) is relied on an felix.
            the first element is where the opc server will be run

        starting this opc requires felixcore.
            to be run on those corresponding felix
        restarting this opc from scratch will certainly requires restarting those felix as well

        killing the corresponding felix will kill all related opc
        """
        self.d_opc_flx[opc] = l_flx
        for flx in l_flx:
            if flx not in self.d_flx_opc:
                self.d_flx_opc[flx] = set()
                pass
            self.d_flx_opc[flx].add(opc)
            pass
        pass

    def kill_chain_flx(self, flx):
        """
        if you kill this felix, you would of course kill those opc
        """
        flx_set = set([flx])
        opc_set = set()
        for opc in self.d_flx_opc[flx]:
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
        for flx in self.d_opc_flx[opc]:
            flx_set.add(flx)
            opc_set.update(self.kill_chain_flx(flx)[1])
            pass
        return flx_set, opc_set



if __name__ == "__main__":
    a = OpcFlxRelationship()
    a.opc_flx(1, ["flx1"])
    a.opc_flx(2, ["flx1"])
    a.opc_flx(3, ["flx1", "flx2"])
    a.opc_flx(4, ["flx2"])
    a.opc_flx(5, ["flx2"])
    a.opc_flx(6, ["flx3", "flx2"])
    a.opc_flx(7, ["flx3"])
    a.opc_flx(8, ["flx3"])
    print(a.kill_chain_flx("flx1"))
