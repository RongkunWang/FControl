import sys
sys.path.append("/atlas-home/1/rowang/NSW/lib/")
import opc_mapping

# for MM
MM_flx_dict = {}
MM_port_dict = {}
for sector, flx in opc_mapping.d_host_mma.items():
    sector = f"A{sector:02d}"
    flxhost, port = flx.split(":")
    MM_flx_dict[sector] = [flxhost]
    MM_port_dict[sector] = port

MM_flx_dict["A03"].append( MM_flx_dict["A05"][0] ) 
MM_flx_dict["A06"].append( MM_flx_dict["A05"][0] ) 

MM_flx_dict["A11"].append( MM_flx_dict["A13"][0] ) 
MM_flx_dict["A14"].append( MM_flx_dict["A13"][0] ) 


for sector, flx in opc_mapping.d_host_mmc.items():
    sector = f"C{sector:02d}"
    flxhost, port = flx.split(":")
    MM_flx_dict[sector] = [flxhost]
    MM_port_dict[sector] = port

MM_flx_dict["C03"].append( MM_flx_dict["C05"][0] ) 
MM_flx_dict["C06"].append( MM_flx_dict["C05"][0] ) 

MM_flx_dict["C11"].append( MM_flx_dict["C13"][0] ) 
MM_flx_dict["C14"].append( MM_flx_dict["C13"][0] ) 



flx_dict  = {}
port_dict = {}

flx_dict["MM"]  = MM_flx_dict
port_dict["MM"] = MM_port_dict

flx_dict["sTGC"] = {}
port_dict["sTGC"] = {}


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
