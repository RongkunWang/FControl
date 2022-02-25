import sys
sys.path.append("/atlas-home/1/rowang/NSW/lib/")
import opc_mapping
import os
USER = os.environ["USER"]
author = "Rongkun Wang <rongkun.wang@cern.ch>"


def getLog(USER, det, sside = "A"):
    if det == "TP":
        return f"/shared/data/{USER}/FControl/TP"
    else:
        return f"/shared/data/{USER}/FControl/{det}-{sside}"

TP_log_dir = getLog(USER, "TP")

#################################################
# GUI
#################################################
ncolflx = 5
ncolopc = 4
ncol = ncolflx + ncolopc  

#################################################
# FLX
#################################################
flx_dict  = {}
port_dict = {}

# for MM
flx_dict["MM"] = {}
port_dict["MM"] = {}
flx_dict["sTGC"] = {}
port_dict["sTGC"] = {}
flx_dict["TP"] = {}
port_dict["TP"] = {}

#  FLX_SETUP = "source /sw/atlas/felix/felix-04-02-00-b4-stand-alone/x86_64-centos7-gcc8-opt/setup.sh"
FLX_SETUP = "source /sw/atlas/felix/felix-04-02-00-b7-rm4-stand-alone/x86_64-centos7-gcc8-opt/setup.sh"
FLX_EXE = "felixcore"
OPC_EXE_DIR = "/det/dcs/Production/ScaOpcUa/bin/"
OPC_EXE = "OpcUaScaServer"

# TODO: felix-id and interface configurable
flx_arg = { "pc-tdq-flx-nsw-mm-{0:02d}.cern.ch".format(key) : "--data-interface vlan413" for key in range(12) }
flx_arg.update({"pc-tdq-flx-nsw-stgc-{0:02d}.cern.ch".format(key) : "--data-interface vlan413" for key in range(16)})
flx_arg.update({"pc-tdq-flx-nsw-tp-a-00.cern.ch" : "--data-interface vlan413 --elink 0-8000 --felix-id 0x30"})
flx_arg.update({"pc-tdq-flx-nsw-tp-c-00.cern.ch" : "--data-interface vlan413 --elink 0-8000 --felix-id 0x31"})

for sector, flx in opc_mapping.d_host_mma.items():
    sector = f"A{sector:02d}"
    flxhost, port = flx.split(":")
    flx_dict["MM"][sector] = [flxhost]
    port_dict["MM"][sector] = port

flx_dict["MM"]["A03"].append( flx_dict["MM"]["A05"][0] ) 
flx_dict["MM"]["A06"].append( flx_dict["MM"]["A05"][0] ) 
flx_dict["MM"]["A11"].append( flx_dict["MM"]["A13"][0] ) 
flx_dict["MM"]["A14"].append( flx_dict["MM"]["A13"][0] ) 

for sector, flx in opc_mapping.d_host_mmc.items():
    sector = f"C{sector:02d}"
    flxhost, port = flx.split(":")
    flx_dict["MM"][sector] = [flxhost]
    port_dict["MM"][sector] = port

flx_dict["MM"]["C03"].append( flx_dict["MM"]["C05"][0] ) 
flx_dict["MM"]["C06"].append( flx_dict["MM"]["C05"][0] ) 
flx_dict["MM"]["C11"].append( flx_dict["MM"]["C13"][0] ) 
flx_dict["MM"]["C14"].append( flx_dict["MM"]["C13"][0] ) 


for sector, flx in opc_mapping.d_host_stgca.items():
    sector = f"A{sector:02d}"
    flxhost, port = flx.split(":")
    flx_dict["sTGC"][sector] = [flxhost]
    port_dict["sTGC"][sector] = port

for sector, flx in opc_mapping.d_host_stgcc.items():
    sector = f"C{sector:02d}"
    flxhost, port = flx.split(":")
    flx_dict["sTGC"][sector] = [flxhost]
    port_dict["sTGC"][sector] = port


flx_dict["TP"]["A"] = ["pc-tdq-flx-nsw-tp-a-00.cern.ch"]
flx_dict["TP"]["C"] = ["pc-tdq-flx-nsw-tp-c-00.cern.ch"]
port_dict["TP"]["A"] = 48020
port_dict["TP"]["C"] = 48020




#################################################
# OPC
#################################################
opc_dict = {}
opc_dict["MM"] = {}
opc_dict["sTGC"] = {}
opc_dict["TP"] = {}
opc_dict["TP"]["A"] = f"{TP_log_dir}/TP-A.xml"
opc_dict["TP"]["C"] = f"{TP_log_dir}/TP-C.xml"

# TODO: auto generate here

OPC_MMA_DIR = "/det/dcs/Development/ATLAS_DCS_MMG/ATLMMGELTXA/config/"
OPC_MMC_DIR = "/det/dcs/Development/ATLAS_DCS_MMG/ATLMMGELTXC/config/"
opc_dict["MM"]["A01"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-00_MMG_A1_OLDNAMING.xml"
opc_dict["MM"]["A02"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-00_MMG_A2_OLDNAMING.xml"
opc_dict["MM"]["A03"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-00_MMG_A3_OLDNAMING.xml"
opc_dict["MM"]["A04"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-01_MMG_A4_OLDNAMING.xml"
opc_dict["MM"]["A05"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-01_MMG_A5_OLDNAMING.xml"
opc_dict["MM"]["A06"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-02_MMG_A6_OLDNAMING.xml"
opc_dict["MM"]["A07"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-02_MMG_A7_OLDNAMING.xml"
opc_dict["MM"]["A08"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-02_MMG_A8_OLDNAMING.xml"

opc_dict["MM"]["A09"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-03_MMG_A9_OLDNAMING.xml"
opc_dict["MM"]["A10"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-03_MMG_A10_OLDNAMING.xml"
opc_dict["MM"]["A11"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-03_MMG_A11_OLDNAMING.xml"
opc_dict["MM"]["A12"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-04_MMG_A12_OLDNAMING.xml"
opc_dict["MM"]["A13"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-04_MMG_A13_OLDNAMING.xml"
opc_dict["MM"]["A14"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-05_MMG_A14_OLDNAMING.xml"
opc_dict["MM"]["A15"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-05_MMG_A15_OLDNAMING.xml"
opc_dict["MM"]["A16"] = OPC_MMA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-05_MMG_A16_OLDNAMING.xml"

opc_dict["MM"]["C01"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-06_MMG_C1_OLDNAMING.xml"
opc_dict["MM"]["C02"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-06_MMG_C2_OLDNAMING.xml"
opc_dict["MM"]["C03"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-06_MMG_C3_OLDNAMING.xml"
opc_dict["MM"]["C04"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-07_MMG_C4_OLDNAMING.xml"
opc_dict["MM"]["C05"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-07_MMG_C5_OLDNAMING.xml"
opc_dict["MM"]["C06"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-08_MMG_C6_OLDNAMING.xml"
opc_dict["MM"]["C07"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-08_MMG_C7_OLDNAMING.xml"
opc_dict["MM"]["C08"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-08_MMG_C8_OLDNAMING.xml"

opc_dict["MM"]["C09"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-09_MMG_C9_OLDNAMING.xml"
opc_dict["MM"]["C10"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-09_MMG_C10_OLDNAMING.xml"
opc_dict["MM"]["C11"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-09_MMG_C11_OLDNAMING.xml"
opc_dict["MM"]["C12"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-10_MMG_C12_OLDNAMING.xml"
opc_dict["MM"]["C13"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-10_MMG_C13_OLDNAMING.xml"
opc_dict["MM"]["C14"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-11_MMG_C14_OLDNAMING.xml"
opc_dict["MM"]["C15"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-11_MMG_C15_OLDNAMING.xml"
opc_dict["MM"]["C16"] = OPC_MMC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-11_MMG_C16_OLDNAMING.xml"

OPC_STGCA_DIR = "/det/dcs/Development/ATLAS_DCS_STG/ATLSTGELTXA/config/"
OPC_STGCC_DIR = "/det/dcs/Development/ATLAS_DCS_STG/ATLSTGELTXC/config/"
opc_dict["sTGC"]["A01"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-00_STG_A1_OLDNAMING.xml"
opc_dict["sTGC"]["A02"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-00_STG_A2_OLDNAMING.xml"
opc_dict["sTGC"]["A03"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-01_STG_A3_OLDNAMING.xml"
opc_dict["sTGC"]["A04"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-01_STG_A4_OLDNAMING.xml"
opc_dict["sTGC"]["A05"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-02_STG_A5_OLDNAMING.xml"
opc_dict["sTGC"]["A06"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-02_STG_A6_OLDNAMING.xml"
opc_dict["sTGC"]["A07"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-03_STG_A7_OLDNAMING.xml"
opc_dict["sTGC"]["A08"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-03_STG_A8_OLDNAMING.xml"
opc_dict["sTGC"]["A09"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-04_STG_A9_OLDNAMING.xml"
opc_dict["sTGC"]["A10"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-04_STG_A10_OLDNAMING.xml"
opc_dict["sTGC"]["A11"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-05_STG_A11_OLDNAMING.xml"
opc_dict["sTGC"]["A12"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-05_STG_A12_OLDNAMING.xml"
opc_dict["sTGC"]["A13"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-06_STG_A13_OLDNAMING.xml"
opc_dict["sTGC"]["A14"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-06_STG_A14_OLDNAMING.xml"
opc_dict["sTGC"]["A15"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-07_STG_A15_OLDNAMING.xml"
opc_dict["sTGC"]["A16"] = OPC_STGCA_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-07_STG_A16_OLDNAMING.xml"
opc_dict["sTGC"]["C01"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-08_STG_C1_OLDNAMING.xml"
opc_dict["sTGC"]["C02"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-08_STG_C2_OLDNAMING.xml"
opc_dict["sTGC"]["C03"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-09_STG_C3_OLDNAMING.xml"
opc_dict["sTGC"]["C04"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-09_STG_C4_OLDNAMING.xml"
opc_dict["sTGC"]["C05"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-10_STG_C5_OLDNAMING.xml"
opc_dict["sTGC"]["C06"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-10_STG_C6_OLDNAMING.xml"
opc_dict["sTGC"]["C07"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-11_STG_C7_OLDNAMING.xml"
opc_dict["sTGC"]["C08"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-11_STG_C8_OLDNAMING.xml"
opc_dict["sTGC"]["C09"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-12_STG_C9_OLDNAMING.xml"
opc_dict["sTGC"]["C10"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-12_STG_C10_OLDNAMING.xml"
opc_dict["sTGC"]["C11"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-13_STG_C11_OLDNAMING.xml"
opc_dict["sTGC"]["C12"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-13_STG_C12_OLDNAMING.xml"
opc_dict["sTGC"]["C13"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-14_STG_C13_OLDNAMING.xml"
opc_dict["sTGC"]["C14"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-14_STG_C14_OLDNAMING.xml"
opc_dict["sTGC"]["C15"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-15_STG_C15_OLDNAMING.xml"
opc_dict["sTGC"]["C16"] = OPC_STGCC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-15_STG_C16_OLDNAMING.xml"

def OpcPort(port):
    return f"--opcua_backend_config /det/dcs/Development/ATLAS_DCS_MUO/muoNswEltxScaOpcConfigTemplates/ServerConfig_{port}.xml"
