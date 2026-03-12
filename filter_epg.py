import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import urllib.request

# 1. ELENCO FONTI (Da italy1 a italy8)
SOURCES = [f"https://www.open-epg.com/files/italy{i}.xml" for i in range(1, 9)]

# 2. I TUOI CANALI (Come scritti nel file M3U)
# Se un canale non appare, aggiungilo qui sotto.
TARGET_CHANNELS = [
    "Rai 1", "Rai 2", "Rai 3", "Rete 4", "Canale 5", "Italia 1", "LA7", 
    "La7 Cinema", "TV8", "NOVE", "Cielo", "Real Time", "Iris", "Cine34", 
    "Rai 4", "Rai Movie", "Twenty Seven", "Rai 5", "La 5", "Giallo", 
    "DMAX", "FOCUS", "Discovery Channel", "HGTV - Home&Garden", 
    "Mediaset Extra", "Italia 2", "Canale 21", "Rakuten Film Top", 
    "Rakuten Film Azione", "Rakuten Film Fantascienza", "Rakuten Film Dramma", 
    "Rakuten Film Romantici", "Rakuten Film Commedia", "NEXO Film Thriller", 
    "NEXO Film Crime", "CHILI Film Alta Tensione", "CHILI Film Romantici", 
    "CHILI Film Grandi Nomi", "Sony One | Film d'azione", 
    "Sony One | Film divertenti", "Sony One | Gli imperdibili", 
    "Sony One | Serie Thriller", "Sony One | Serie da Ridere"
]

# 3. MAPPATURA MANUALE (Per casi difficili)
# "Nome_nel_file_XML": "Nome_nella_tua_lista"
MAPPING = {
    "Rai 1 (ITA).it": "Rai 1",
    "LA 7.it": "LA7",
    "NOVE (ITA).it": "NOVE",
    "SonyOne|Filmd'azione.it": "Sony One | Film d'azione",
    "SonyOne|Filmdivertenti.it": "Sony One | Film divertenti"
}

TIME_SHIFT = 1 # Spostamento orario (+1 ora)

def fix_time(time_str):
    try:
        fmt = "%Y%m%d%H%M%S"
        parts = time_str.split(" ")
        dt = datetime.strptime(parts[0], fmt) + timedelta(hours=TIME_SHIFT)
        return dt.strftime(fmt) + " " + parts[1]
    except: return time_str

new_root = ET.Element("tv", {"generator-info-name": "GitHub_EPG_Processor"})
added_channels = set()

for url in SOURCES:
    try:
        print(f"Elaborazione: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            tree = ET.parse(response)
            root = tree.getroot()

            # Passaggio 1: Canali
            for channel in root.findall("channel"):
                orig_id = channel.get("id")
                clean_id = orig_id.replace(".it", "").strip()
                
                # Cerchiamo corrispondenza nel Mapping o nella lista Target
                target_name = MAPPING.get(orig_id) or next((tc for tc in TARGET_CHANNELS if tc.lower() == clean_id.lower()), None)
                
                if target_name and target_name not in added_channels:
                    channel.set("id", target_name)
                    disp = channel.find("display-name")
                    if disp is not None: disp.text = target_name
                    new_root.append(channel)
                    added_channels.add(target_name)

            # Passaggio 2: Programmi
            for prog in root.findall("programme"):
                orig_id = prog.get("channel")
                clean_id = orig_id.replace(".it", "").strip()
                
                target_name = MAPPING.get(orig_id) or next((tc for tc in TARGET_CHANNELS if tc.lower() == clean_id.lower()), None)
                
                if target_name:
                    prog.set("channel", target_name)
                    prog.set("start", fix_time(prog.get("start")))
                    prog.set("stop", fix_time(prog.get("stop")))
                    new_root.append(prog)
    except Exception as e:
        print(f"Salto {url} causa errore: {e}")

# Scrittura file finale
ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
print(f"Completato! Canali trovati: {len(added_channels)}")
