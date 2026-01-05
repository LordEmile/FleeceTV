from fastapi import APIRouter, HTTPException

route_serie = APIRouter(prefix="/serie")


#ajouter une nouvelle serie/saison/episode
@route_serie.post("/")
async def add_serie():
    return "a venir"

@route_serie.post("/{id}/season")
async def add_season():
    return "a venir"

@route_serie.post("/{serie_id}/{season_id}/episode")
async def add_episode():
    return "a venir"


#afficher information
@route_serie.get("/")
async def get_all_serie():
    return "a venir"

@route_serie.get("/{id}")
async def get_serie_by_id():
    return "a venir"

@route_serie.get("/{serie_id}/{season_id}")
async def get_season_by_id():
    return "a venir"


#joué une serie
@route_serie.get("/stream/{serie_id}/{season_id}/{episode_id}/{language}")
async def play_serie():
    return "a venir"