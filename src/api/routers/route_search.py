from fastapi import APIRouter, HTTPException

route_search = APIRouter(prefix="/search")

#recherche par filtre
@route_search.get("/{mot_clé}")
async def get_by_motcle():
    return "a venir"

@route_search.get("/{category}")
async def get_by_category():
    return "a venir"


#20 serie/film les plus recent
@route_search.get("/top")
async def get_by_date():
    return "a venir"