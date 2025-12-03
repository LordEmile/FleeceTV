import xml.etree.ElementTree as ET

async def filter_movie_torrent(xml, params):
    TRADUCTION = ["FRENCH", "TRUEFRENCH", "VF"]
    VO = ["VOSTFR"]
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
        has_integral = any(i in title.upper() for i in INTEGRAL)
        has_multi = any(m in title.upper() for m in MULTI)
        has_trad = any(t in title.upper() for t in TRADUCTION)
        has_vo = any(v in title.upper() for v in VO) 
        if seeders <=5 or not has_qual:
            continue
        if has_integral and has_multi and params not in ("VF", "VOSTFR"):
            result.append(i)
            isIntegral = True
            isMultiLang = True
            break
        elif has_multi and params not in ("VF", "VOSTFR"):
            result.append(i)
            isMultiLang = True
            break
        elif has_trad and params != "VOSTFR":
            result.append(i)
            lang = "vf"
            break
        elif has_vo and params != "VF":
            result.append(i)
            lang = "vostfr"
            break
    return result[0], isIntegral, isMultiLang, lang
