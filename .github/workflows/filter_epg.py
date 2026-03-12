import xml.etree.ElementTree as ET

keys = ["Rai", "Mediaset", "Rete 4", "Canale 5", "Italia 1", "Italia 2", "La7", "Tv8", "Nove", "Cielo", "Iris", "DMAX", "Focus", "Giallo", "Cine34", "Real Time", "Twenty Seven", "TwentySeven", "Discovery", "HGTV"]

try:
    tree = ET.parse("temp_guida.xml")
    root = tree.getroot()
    new_root = ET.Element("tv", root.attrib)
    matched_ids = []
    
    for channel in root.findall("channel"):
        chid = channel.get("id")
        if chid and any(k.lower() in chid.lower() for k in keys):
            new_root.append(channel)
            matched_ids.append(chid)
            
    for prog in root.findall("programme"):
        if prog.get("channel") in matched_ids:
            new_root.append(prog)
            
    ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
    print("Filtraggio completato con successo.")
except Exception as e:
    print(f"Errore: {e}")
