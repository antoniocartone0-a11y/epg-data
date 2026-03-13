import gzip
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

SOURCE_URL = "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz"
TIME_SHIFT = 1 

# MAPPATURA: "ID_SORGENTE_EPG_RIPPER" : "TUO_ID_M3U"
MAPPING = {
    "Rai.1.it": "Rai 1.it",
    "Rai.2.it": "Rai 2.it",
    "Rai.3.it": "Rai 3.it",
    "Rete.4.it": "Rete 4.it",
    "Canale.5.it": "Canale 5.it",
    "Italia.1.it": "Italia 1.it",
    "La7.it": "LA7.it",
    "La7d.it": "La7d.it",
    "Tv8.it": "TV8.it",
    "Nove.it": "NOVE.it",
    "Cielo.it": "Cielo.it",
    "Real.Time.it": "Real Time.it",
    "Iris.it": "Iris.it",
    "Cine34.it": "Cine34.it",
    "Rai.4.it": "Rai 4.it",
    "Rai.Movie.it": "Rai Movie.it",
    "Canale.20.it": "canale 20.it",
    "Twenty.Seven.it": "Twenty Seven.it",
    "Rai.5.it": "Rai 5.it",
    "La.5.it": "La 5.it",
    "Giallo.it": "Giallo.it",
    "DMAX.it": "DMAX.it",
    "Focus.it": "FOCUS.it",
    "Discovery.Channel.it": "Discovery Channel.it",
    "HGTV.it": "HGTV - Home&Garden.it",
    "Mediaset.Extra.it": "Mediaset Extra.it",
    "Italia.2.it": "Italia 2.it",
    "Canale.21.it": "Canale 21.it"
}

def fix_time(time_str):
    try:
        fmt = "%Y%m%d%H%M%S"
        parts = time_str.split(" ")
        dt = datetime.strptime(parts[0], fmt) + timedelta(hours=TIME_SHIFT)
        return dt.strftime(fmt) + " " + parts[1]
    except: return time_str

def main():
    print("Scaricamento e decompressione...")
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    
    with gzip.GzipFile(fileobj=response) as uncompressed:
        tree = ET.parse(uncompressed)
        root = tree.getroot()

    new_root = ET.Element("tv", {"generator-info-name": "EPG_Optimizer_V2"})
    
    # 1. Creazione Canali
    for channel in root.findall("channel"):
        orig_id = channel.get("id")
        if orig_id in MAPPING:
            new_ch = ET.SubElement(new_root, "channel", {"id": MAPPING[orig_id]})
            for child in channel:
                # Copiamo display-name, icon, etc.
                new_ch.append(child)

    # 2. Creazione Programmi
    for prog in root.findall("programme"):
        orig_id = prog.get("channel")
        if orig_id in MAPPING:
            p_attrib = prog.attrib.copy()
            p_attrib["channel"] = MAPPING[orig_id]
            p_attrib["start"] = fix_time(p_attrib["start"])
            p_attrib["stop"] = fix_time(p_attrib["stop"])
            
            new_prog = ET.SubElement(new_root, "programme", p_attrib)
            for child in prog:
                new_prog.append(child)

    # Salvataggio
    ET.indent(new_root, space="  ", level=0)
    ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
    print("Completato!")

if __name__ == "__main__":
    main()
