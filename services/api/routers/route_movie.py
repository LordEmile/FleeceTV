from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from shemas.shema_movie import movieCreate
from service.service_movie import get_movie_by_id, get_movie_by_title, get_all_movie, create_movie

route_movie = APIRouter(prefix="/movie")


#ajouter un nouveau film
@route_movie.post("/", status_code=201)
async def add_movie(data:movieCreate, db:Session=Depends(get_db)):
    return await create_movie(data=data, db=db) 


#afficher information
@route_movie.get("/")
async def get_movies(db:Session=Depends(get_db)):
    movies = await get_all_movie(db=db)
    if not movies:
        raise HTTPException(status_code=404, detail="No Movies Yet")
    return movies

@route_movie.get("/id/{id}")
async def get_movie_by(id:int, db:Session=Depends(get_db)):
    movie = await get_movie_by_id(db=db, movie_id=id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    return movie

@route_movie.get("/title/{title}")
async def get_movie(title:str, db:Session=Depends(get_db)):
    movie = await get_movie_by_title(db=db, movie_name=title)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    return movie


#joué un film
@route_movie.get("/stream/{id}")
async def play_movie():
    return "a venir"