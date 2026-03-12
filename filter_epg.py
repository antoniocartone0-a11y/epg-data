import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import urllib.request

# Sorgenti da italy1 a italy8
SOURCES = [f"https://www.open-epg.com/files/italy{i}.xml" for i in range(1, 9)]

# Mappatura: "ID_SORGENTE_XML": "TUO_ID_M3U"
MAPPING = {
    "Rai 1 (ITA).it": "Rai 1.it",
    "Rai 2 (ITA).it": "Rai 2.it",
    "Rai 3 (ITA).it": "Rai 3.it",
    "Rete 4 (ITA).it": "Rete 4.it",
    "Canale 5 (ITA).it": "Canale 5.it",
    "Italia 1 (ITA).it": "Italia 1.it",
    "La 7.it": "LA7.it",
    "TV8 (ITA).it": "TV8.it",
    "NOVE (ITA).it": "NOVE.it",
    "Cielo (ITA).it": "Cielo.it",
    "Real Time (ITA).it": "Real Time.it",
    "Iris (ITA).it": "Iris.it",
    "Cine34 (ITA).it": "Cine34.it",
    "Rai 4 (ITA).it": "Rai 4.it",
    "Rai Movie (ITA).it": "Rai Movie.it",
    "20 Mediaset.it": "canale 20.it",
    "SonyOne|Filmd'azione.it": "SonyOne|Filmd'azione.it",
    "SonyOne|Filmdivertenti.it": "SonyOne|Filmdivertenti.it"
}

TIME_SHIFT = 1 

def fix_time(time_str):
    try:
        fmt = "%Y%m%d%H%M%S"
        parts = time_str.split(" ")
        dt = datetime.strptime(parts[0], fmt) + timedelta(hours=TIME_SHIFT)
        return dt.strftime(fmt) + " " + parts[1]
    except: return time_str

new_root = ET.Element("tv", {"generator-info-name": "EPG_Auto_Fix"})
added_channels = set()

for url in SOURCES:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            for channel in root.findall("channel"):
                orig_id = channel.get("id")
                if orig_id in MAPPING and MAPPING[orig_id] not in added_channels:
                    channel.set("id", MAPPING[orig_id])
                    new_root.append(channel)
                    added_channels.add(MAPPING[orig_id])
            for prog in root.findall("programme"):
                orig_id = prog.get("channel")
                if orig_id in MAPPING:
                    prog.set("channel", MAPPING[orig_id])
                    prog.set("start", fix_time(prog.get("start")))
                    prog.set("stop", fix_time(prog.get("stop")))
                    new_root.append(prog)
    except: continue

ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
