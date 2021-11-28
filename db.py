import sys
sys.path.append("/atlas-home/1/rowang/NSW/lib/")
import opc_mapping

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

FLX_SETUP = "source /sw/atlas/felix/felix-04-02-00-b4-stand-alone/x86_64-centos7-gcc8-opt/setup.sh"
FLX_EXE = "felixcore"
OPC_EXE = "/det/dcs/Production/ScaOpcUa/bin/OpcUaScaServer"

# TODO: felix-id
# TODO: interface configurable
flx_arg = { "pc-tdq-flx-nsw-mm-{0:02d}.cern.ch".format(key) : "--data-interface vlan413" for key in range(12) }

flx_arg.update({ "pc-tdq-flx-nsw-stgc-{0:02d}.cern.ch".format(key) : "--data-interface vlan413" for key in range(16) })

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


#################################################
# OPC
#################################################

opc_dict = {}
opc_dict["MM"] = {}
opc_dict["sTGC"] = {}

OPC_MM_DIR = "/det/dcs/Development/ATLAS_DCS_MMG/ATLMMGELTXA/config/"
opc_dict["MM"]["A01"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-00_MMG_A1_OLDNAMING.xml"
opc_dict["MM"]["A02"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-00_MMG_A2_OLDNAMING.xml"
opc_dict["MM"]["A03"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-00_MMG_A3_OLDNAMING.xml"
opc_dict["MM"]["A04"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-01_MMG_A4_OLDNAMING.xml"
opc_dict["MM"]["A05"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-01_MMG_A5_OLDNAMING.xml"
opc_dict["MM"]["A06"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-02_MMG_A6_OLDNAMING.xml"
opc_dict["MM"]["A07"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-02_MMG_A7_OLDNAMING.xml"
opc_dict["MM"]["A08"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-02_MMG_A8_OLDNAMING.xml"

opc_dict["MM"]["A09"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-03_MMG_A9_OLDNAMING.xml"
opc_dict["MM"]["A10"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-03_MMG_A10_OLDNAMING.xml"
opc_dict["MM"]["A11"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-03_MMG_A11_OLDNAMING.xml"
opc_dict["MM"]["A12"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-04_MMG_A12_OLDNAMING.xml"
opc_dict["MM"]["A13"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-04_MMG_A13_OLDNAMING.xml"
opc_dict["MM"]["A14"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-05_MMG_A14_OLDNAMING.xml"
opc_dict["MM"]["A15"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-05_MMG_A15_OLDNAMING.xml"
opc_dict["MM"]["A16"] = OPC_MM_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-mm-05_MMG_A16_OLDNAMING.xml"

OPC_STGC_DIR = "/det/dcs/Development/ATLAS_DCS_STG/ATLSTGELTXA/config/"
opc_dict["sTGC"]["A01"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-00_STG_A1_OLDNAMING.xml"
opc_dict["sTGC"]["A02"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-00_STG_A2_OLDNAMING.xml"
opc_dict["sTGC"]["A03"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-01_STG_A3_OLDNAMING.xml"
opc_dict["sTGC"]["A04"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-01_STG_A4_OLDNAMING.xml"
opc_dict["sTGC"]["A05"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-02_STG_A5_OLDNAMING.xml"
opc_dict["sTGC"]["A06"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-02_STG_A6_OLDNAMING.xml"
opc_dict["sTGC"]["A07"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-03_STG_A7_OLDNAMING.xml"
opc_dict["sTGC"]["A08"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-03_STG_A8_OLDNAMING.xml"

opc_dict["sTGC"]["A09"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-04_STG_A9_OLDNAMING.xml"
opc_dict["sTGC"]["A10"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-04_STG_A10_OLDNAMING.xml"
opc_dict["sTGC"]["A11"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-05_STG_A11_OLDNAMING.xml"
opc_dict["sTGC"]["A12"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-05_STG_A12_OLDNAMING.xml"
opc_dict["sTGC"]["A13"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-06_STG_A13_OLDNAMING.xml"
opc_dict["sTGC"]["A14"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-06_STG_A14_OLDNAMING.xml"
opc_dict["sTGC"]["A15"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-07_STG_A15_OLDNAMING.xml"
opc_dict["sTGC"]["A16"] = OPC_STGC_DIR + "ScaOpcUaServer_pc-tdq-flx-nsw-stgc-07_STG_A16_OLDNAMING.xml"


def OpcPort(port):
    return f"--opcua_backend_config /det/dcs/Development/ATLAS_DCS_MUO/muoNswEltxScaOpcConfigTemplates/ServerConfig_{port}.xml"
