import db

from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QSizePolicy
from OpcFlxRelation import OpcFlxRelation


class MM(QWidget, OpcFlxRelation):
    def __init__(self, det = "MM", side = 0):
        QWidget.__init__(self)
        OpcFlxRelation.__init__(self)
        for sector, l_flx in db.flx_dict[det].items():
            self.opc_flx(sector, l_flx, db.port_dict[det][sector])

        self.layout_main = QGridLayout(self)

        self.but_init_all = QPushButton(self)
        self.but_init_all.setText("Init All")
        self.but_restart_failed = QPushButton(self)
        self.but_restart_failed.setText("Restart Failed")
        self.layout_main.addWidget(self.but_init_all, 0, 0, 1, 1)
        self.layout_main.addWidget(self.but_restart_failed, 0, 2, 1, 1)

        self.layout_but = QGridLayout()
        self.layout_main.addLayout(self.layout_but, 1, 0, 1, 6)

        self.l_flx_but = []
        self.l_opc_but = []

        nrow = 0
        # col 0:2
        for i, flx in enumerate(self.return_list_flx()[side]):
            # this button is for checking log
            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, 
                    QSizePolicy.Minimum)
            self.l_flx_but.append( but )
            but.setText(flx)
            but.setObjectName(flx)
            rowspan = len(self.kill_chain_flx(flx)[1])
            #  rowspan = 3
            self.layout_but.addWidget( self.l_flx_but[-1], nrow, 0, rowspan, 1)
            nrow += rowspan

        # col 2:3
        nrow = 0
        for i, sector in enumerate(self.return_list_opc()[side]):
            but = QPushButton(self)
            but.setSizePolicy(QSizePolicy.Minimum, 
                    QSizePolicy.Minimum)
            but.setText("Opc " + sector)
            but.setObjectName(sector)
            rowspan = len(self.d_opc_flx[sector])
            self.l_opc_but.append( but )
            self.layout_but.addWidget( self.l_opc_but[-1], nrow, 1, rowspan, 1)
            nrow += rowspan
            pass

        pass
    pass

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    m = MM()
    print()
    print(m.kill_chain_flx("pc-tdq-flx-nsw-mm-00.cern.ch"))
    print(m.restart_chain_opc("A03"))
