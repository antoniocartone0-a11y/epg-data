import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import urllib.request

# Usiamo solo italy3
SOURCE = "https://www.open-epg.com/files/italy3.xml"

# MAPPATURA: "ID_SORGENTE_XML" : "TUO_ID_M3U"
MAPPING = {
    "Rai 1.it": "Rai 1.it",
    "Rai 2.it": "Rai 2.it",
    "Rai 3.it": "Rai 3.it",
    "Rete 4.it": "Rete 4.it",
    "Canale 5.it": "Canale 5.it",
    "Italia 1.it": "Italia 1.it",
    "LA7.it": "LA7.it",
    "La7 Cinema.it": "La7 Cinema.it",
    "TV8.it": "TV8.it",
    "NOVE.it": "NOVE.it",
    "Cielo.it": "Cielo.it",
    "Real Time.it": "Real Time.it",
    "Iris.it": "Iris.it",
    "Cine34.it": "Cine34.it",
    "Rai 4.it": "Rai 4.it",
    "Rai Movie.it": "Rai Movie.it",
    "Twenty Seven.it": "Twenty Seven.it",
    "Rai 5.it": "Rai 5.it",
    "La 5.it": "La 5.it",
    "Giallo.it": "Giallo.it",
    "DMAX.it": "DMAX.it",
    "FOCUS.it": "FOCUS.it",
    "Discovery Channel.it": "Discovery Channel.it",
    "HGTV - Home&Garden.it": "HGTV - Home&Garden.it",
    "Mediaset Extra.it": "Mediaset Extra.it",
    "Italia 2.it": "Italia 2.it",
    "Canale 21.it": "Canale 21.it",
    "canale 20.it": "canale 20.it",
    "SonyOne|Filmd'azione.it": "SonyOne|Filmd'azione.it",
    "SonyOne|Filmdivertenti.it": "SonyOne|Filmdivertenti.it",
    "SonyOne|Gliimperdibili.it": "SonyOne|Gliimperdibili.it",
    "SonyOne|SerieThriller.it": "SonyOne|SerieThriller.it",
    "SonyOne|SeriedaRidere.it": "SonyOne|SeriedaRidere.it"
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

try:
    req = urllib.request.Request(SOURCE, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        tree = ET.parse(response)
        root = tree.getroot()
        
        # 1. Canali
        for channel in root.findall("channel"):
            orig_id = channel.get("id")
            if orig_id in MAPPING:
                new_ch = ET.SubElement(new_root, "channel", {"id": MAPPING[orig_id]})
                dn = ET.SubElement(new_ch, "display-name")
                dn.text = MAPPING[orig_id]
                added_channels.add(MAPPING[orig_id])
        
        # 2. Programmi
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
except Exception as e:
    print(f"Errore: {e}")

ET.indent(new_root, space="  ", level=0)
ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
