import xml.etree.ElementTree as ET
from fastapi import HTTPException

#trie l'ensemble des torrent donné pour retourné uniquemet celui demandé
async def filter_movie_torrent(xml, params:str | None=None):
    TRADUCTION = ["FRENCH", "TRUEFRENCH", "VF"]
    VO = ["VOSTFR"]
    MULTI = ["MULTI"]
    INTEGRAL = ["INTERGRALE","INTEGRALES","(INTEGRALE)", "(INTEGRALES)", "TRILOGIE", "(TRILOGIE)","HEPTALOGY" ,"HEXALOGIE", "(HEXALOGIE)", "(HEPTALOGY)"]
    QUAL = ["1080", "1080P","1080p" ,"DVDRIP"]
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        raise HTTPException(status_code=502, detail=f"FILTER: invalid XML: {str(e)}")
    liste = []
    result = []
    isMultiLang = False
    isIntegral = False
    lang = ""

    for i in root.findall(".//item"):
        title = i.findtext("title", "").strip()
        enclosure = i.find("enclosure")
        link = enclosure.get("url") if enclosure is not None else None
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
        if seeders < 4 or not has_qual:
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
    if not result:
        raise HTTPException(status_code=500, detail="FILTER : failed")
    return result[0], isIntegral, isMultiLang, lang
