import gzip
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Sorgente professionale EPGShare01
SOURCE_URL = "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz"
TIME_SHIFT = 1  # Aggiunge 1 ora per l'Italia

# MAPPATURA PRECISA: "ID_SORGENTE" : "ID_DESTINAZIONE_M3U"
# Se vuoi che l'ID rimanga identico alla sorgente (con i punti), 
# scrivi lo stesso nome a destra e a sinistra.
CHANNELS_TO_EXTRACT = {
    "Rai.1.it": "Rai.1.it",
    "Rai.2.it": "Rai.2.it",
    "Rai.3.it": "Rai.3.it",
    "Rete.4.it": "Rete.4.it",
    "Canale.5.it": "Canale.5.it",
    "Italia.1.it": "Italia.1.it",
    "La7.it": "La7.it",
    "La7d.it": "La7d.it",
    "Tv8.it": "Tv8.it",
    "Nove.it": "Nove.it",
    "Cielo.it": "Cielo.it",
    "Real.Time.it": "Real.Time.it",
    "Iris.it": "Iris.it",
    "Cine34.it": "Cine34.it",
    "Rai.4.it": "Rai.4.it",
    "Rai.Movie.it": "Rai.Movie.it",
    "Canale.20.it": "Canale.20.it",
    "Twenty.Seven.it": "Twenty.Seven.it",
    "Rai.5.it": "Rai.5.it",
    "La.5.it": "La.5.it",
    "Giallo.it": "Giallo.it",
    "DMAX.it": "DMAX.it",
    "Focus.it": "Focus.it",
    "Discovery.Channel.it": "Discovery.Channel.it",
    "HGTV.it": "HGTV.it",
    "Mediaset.Extra.it": "Mediaset.Extra.it",
    "Italia.2.it": "Italia.2.it",
    "Canale.21.it": "Canale.21.it"
}

def fix_time(time_str):
    try:
        fmt = "%Y%m%d%H%M%S"
        parts = time_str.split(" ")
        dt = datetime.strptime(parts[0], fmt) + timedelta(hours=TIME_SHIFT)
        return dt.strftime(fmt) + " " + parts[1]
    except:
        return time_str

def main():
    print(f"Scaricamento in corso da: {SOURCE_URL}")
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            with gzip.GzipFile(fileobj=response) as uncompressed:
                tree = ET.parse(uncompressed)
                root = tree.getroot()
    except Exception as e:
        print(f"Errore nel download o decompressione: {e}")
        return

    new_root = ET.Element("tv", {"generator-info-name": "EPG_Custom_Filter"})
    
    # 1. Estrazione Canali
    for channel in root.findall("channel"):
        orig_id = channel.get("id")
        if orig_id in CHANNELS_TO_EXTRACT:
            # Crea un nuovo elemento channel con l'ID scelto
            new_id = CHANNELS_TO_EXTRACT[orig_id]
            new_ch = ET.SubElement(new_root, "channel", {"id": new_id})
            # Copia tutti i sotto-elementi (display-name, icon, url)
            for child in channel:
                new_ch.append(child)

    # 2. Estrazione Programmi
    for prog in root.findall("programme"):
        channel_id = prog.get("channel")
        if channel_id in CHANNELS_TO_EXTRACT:
            # Crea una copia del programma
            new_id = CHANNELS_TO_EXTRACT[channel_id]
            p_attrib = prog.attrib.copy()
            p_attrib["channel"] = new_id
            p_attrib["start"] = fix_time(p_attrib.get("start", ""))
            p_attrib["stop"] = fix_time(p_attrib.get("stop", ""))
            
            new_prog = ET.SubElement(new_root, "programme", p_attrib)
            for child in prog:
                new_prog.append(child)

    # Salvataggio file finale
    ET.indent(new_root, space="  ", level=0)
    ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
    print("Guida creata con successo!")

if __name__ == "__main__":
    main()
