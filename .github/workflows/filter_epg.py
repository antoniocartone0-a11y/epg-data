import xml.etree.ElementTree as ET
keys = ["Rai", "Mediaset", "Rete 4", "Canale 5", "Italia 1", "Italia 2", "La7", "Tv8", "Nove", "Cielo", "Iris", "DMAX", "Focus", "Giallo", "Cine34", "Real Time", "Twenty Seven", "TwentySeven", "Discovery", "HGTV"]
try:
    tree = ET.parse("temp_guida.xml")
    root = tree.getroot()
    new_root = ET.Element("tv", root.attrib)
    matched_ids = []
    for ch in root.findall("channel"):
        chid = ch.get("id")
        if chid and any(k.lower() in chid.lower() for k in keys):
            new_root.append(ch)
            matched_ids.append(chid)
    for pg in root.findall("programme"):
        if pg.get("channel") in matched_ids:
            new_root.append(pg)
    ET.ElementTree(new_root).write("guida.xml", encoding="UTF-8", xml_declaration=True)
except Exception as e:
    print(e)
