import xml.etree.ElementTree as ET

async def filter_movie_torrent(xml):
    VF = ["FRENCH", "TRUEFRENCH", "VF"]
    VOSTF = ["VOSTFR"]
    MULTI = ["MULTI", ]
    INTEGRAL = ["integrale", "integrales", "trilogie"]
    QUAL = ["1080"]

    root = ET.fromstring(xml.text)
    liste = []

    result = []
    isMultiLang = False
    isIntegral = False
    lang = ""

    for i in root.findall(".//item"):
        title = i.findtext("title", "").strip()
        link = i.findtext("link", "")
        size_text = i.findtext("size")
        size = int(size_text) if size_text else None
        seeders = 0
        for attr in i.findall(".//{*}attr"):
            if attr.attrib.get("name") == "seeders":
                seeders = int(attr.attrib.get("value", "0"))
        liste.append({
            "title": title,
            "link": link,
            "size": size,
            "seeders": seeders,
        })

    for i in liste:
        title = i["title"]
        seeders = i["seeders"]
        has_qual = any(q in title.upper() for q in QUAL)
