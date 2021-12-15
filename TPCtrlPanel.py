from functools import partial

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QMessageBox, QDialog, QCheckBox,
        QPushButton, QSizePolicy, QRadioButton, QGroupBox, QComboBox, QLabel)

import db, utilities
from CtrlPanel import CtrlPanel

class TPCtrlPanel(CtrlPanel):
    class CBDialog(QDialog):
        def __init__(self, parent, text, lsectors, det):
            self.det = det
            QDialog.__init__(self, parent)
            self._layout = QGridLayout(self)
            self.setWindowTitle(text)
            self.setCB(lsectors)
            self.setTwoButtons()

        @property
        def layout(self):
            return self._layout
            pass

        def setCB(self, lsectors):
            self.l_cb = []
            gb = QGroupBox("technology")
            rb1 = QRadioButton("comb")
            rb2 = QRadioButton("mm")
            rb3 = QRadioButton("stgc")
            l_rb = [rb1, rb2, rb3]
            # setting the checkboxes first
            @QtCore.pyqtSlot()
            def setter(rb):
                self.det = rb.text()
            for rb in l_rb:
                rb.toggled.connect(partial(setter, rb))
                #  print(rb.text())
                if rb.text() == self.det:
                    #  print("match")
                    rb.setChecked(True)
            vbox = QHBoxLayout()
            vbox.addWidget(rb1)
            vbox.addWidget(rb2)
            vbox.addWidget(rb3)
            vbox.addStretch(1)
            gb.setLayout(vbox)
            self.layout.addWidget(gb, 0, 0, 1, 8)

            cb_all = QCheckBox("all")
            self.layout.addWidget(cb_all, 1, 0, 1, 8)
            for i in range(1, 17):
                cb = QCheckBox(f"{i}")
                self.l_cb.append(cb)
                self.layout.addWidget(cb, (i - 1) // 8 + 2, (i - 1) % 8, 1, 1)
                if i in lsectors:
                    cb.setCheckState(QtCore.Qt.Checked)
            @QtCore.pyqtSlot(int)
            def toggle_all(state):
                for cb in self.l_cb:
                    cb.setCheckState(state)
            cb_all.stateChanged.connect(partial(toggle_all))

        def exec(self):
            # TODO: return detector type
            if not QDialog.exec(self):
                return 0
            return [int(cb.text()) for cb in self.l_cb if cb.isChecked()], self.det
            pass

        def setTwoButtons(self):
            cb1 = QPushButton("OK")
            cb2 = QPushButton("Cancel")
            self.layout.addWidget(cb1, 4, 0, 1, 4)
            self.layout.addWidget(cb2, 4, 4, 1, 4)

            cb1.clicked.connect(self.accept)
            cb2.clicked.connect(self.reject)
            #  cb2.clicked.connect(partial(click_cancel))
            pass
        pass

    def __init__(self, *args):
        QWidget.__init__(self)
        #  self.setStyleSheet(" background-color:cyan")
        self.layout_main2 = QGridLayout(self)
        self.layout_main = QGridLayout()

        self.flx_host = {
                "A": db.flx_dict["TP"]["A"][0], 
                "C": db.flx_dict["TP"]["C"][0], 
                }
        self.enabled = {"A":[], "C":[]}
        self.tech = {"A":"comb", "C":"comb"}


        self.sel_sec_A = QPushButton("Select A sectors")
        self.sel_sec_A.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.sel_sec_A.clicked.connect(partial(self.resolve_sectors, "A"))
        self.layout_main2.addWidget(self.sel_sec_A, 0, 0, 1, 1)

        self.label = {}
        self.label["A"] = QLabel("Current: comb ")
        self.layout_main2.addWidget(self.label["A"], 0, 1, 1, 3)

        self.sel_sec_C = QPushButton("Select C sectors")
        self.sel_sec_C.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.sel_sec_C.clicked.connect(partial(self.resolve_sectors, "C"))
        self.layout_main2.addWidget(self.sel_sec_C, 0, 4, 1, 1)

        self.label["C"] = QLabel("Current: comb ")
        self.layout_main2.addWidget(self.label["C"], 0, 5, 1, 3)



        self.part_name = QComboBox()
        self.part_name.addItem("part-NSW-MMTP-SideA")
        self.part_name.addItem("part-NSW-MMTP-SideC")
        self.layout_main2.addWidget(self.part_name, 1, 0, 1, 2)

        self.calib_type = QComboBox()
        self.calib_type.addItem("MMStaircase")
        self.calib_type.addItem("MMTPInputPhase")
        self.calib_type.addItem("MMCableNoise")
        self.calib_type.addItem("MMARTConnectivityTest")
        self.calib_type.addItem("MMARTPhase")
        self.layout_main2.addWidget(self.calib_type, 1, 2, 1, 2)

        self.isSend = QPushButton("Send IS Config")
        self.layout_main2.addWidget(self.isSend, 1, 4, 1, 1)
        @QtCore.pyqtSlot()
        def is_write():
            job = QtCore.QProcess()
            job.start(f"is_write -p {self.part_name.currentText()} -n NswParams.Calib.calibType -t String -i 0 -v {self.calib_type.currentText()}")
            job.waitForFinished(5000)
            pass
            #  os.system

        self.isSend.clicked.connect(partial(is_write))

        self.layout_main2.addLayout(self.layout_main, 2, 0, 1, db.ncol)

        super().__init__(*args)

        pass

    @QtCore.pyqtSlot(bool)
    def resolve_sectors(self, side):
        """
        put sectors to init and run command
         elink and generate opc.
        """
        ret = self.CBDialog(self, f"Side {side}", self.enabled[side], self.tech[side]).exec()
        if ret == 0:
           return 

        self.enabled[side] = ret[0]
        self.tech[side] = ret[1]

        flxserver = self.return_list_flx()[self.flx_host[side]]
        opcserver = self.return_list_opc()[side]

        l_sec_str = " ".join([str(i) for i in self.enabled[side]])

        self.label[side].setText(f"Current: {self.tech[side]} {l_sec_str}")
        # TODO: Use not label, but select box?

        if len(l_sec_str) == 0:
            l_sec_str = [0]
        
        flxserver.init_command = f"{flxserver.original_init_command} && /atlas-home/1/rowang/NSW/elink/feconf.py -s {l_sec_str} -i -t {self.tech[side]}" 
        #  print(flxserver.init_command)
        opcserver.run_command = f"{opcserver.original_init_command} && /atlas-home/1/rowang/NSW/opc/generate.py -s {l_sec_str} -S {side} -t {self.tech[side]} -o {db.opc_dict['TP'][side]} && {opcserver.original_run_command}" 
        #  print(opcserver.run_command)
        pass
    pass
