from fastapi import APIRouter, HTTPException

route_movie = APIRouter(prefix="/movie")


#ajouter un nouveau film
@route_movie.post("/")
async def add_movie():
    return "a venir"


#afficher information
@route_movie.get("/")
async def get_all_movie():
    return "a venir"

@route_movie.get("/{id}")
async def get_movie_by_id():
    return "a venir"


#joué un film
@route_movie.get("/stream/{id}/{language}")
async def play_movie():
    return "a venir"