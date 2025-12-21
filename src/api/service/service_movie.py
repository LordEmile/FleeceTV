import os
import httpx
import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session
from api.models.movie import Movie
from api.models.files import File
from fastapi import HTTPException
from api.models.enum.language import EnumLanguage
from api.service.service_filter import filter_movie_torrent
from api.shemas.shema_movie import movieCreate, movieResponce
from api.service.service_files import * 

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
JACKETT_KEY = os.getenv("JACKETT_KEY")


#recherche de film a partir de l'api tmdb
async def search_movie_tmdb(title : str, years : str):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "query" : title,
        "primary_release_year" : years,
        "api_key" : API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            raise HTTPException(status_code=400, detail="TMDB : Movie not found")
        return results[0]
    

#recherche de torrentsa partir de l'api(local) jackett
async def search_movie_torrent(title : str):
    url = "http://jackett:9117/api/v2.0/indexers/all/results/torznab"
    params = {
        "apikey": JACKETT_KEY,
        "t": "movie",
        "q": title,
        "cat": "2000"
    }
    async with httpx.AsyncClient() as client:
        liste = await client.get(url, params=params)
        liste.raise_for_status()
        xml_text = liste.text
        if "<item>" not in xml_text:
            raise HTTPException(status_code=404, detail="JACKETT: Torrent not found")
    return xml_text
        

#création d'un nouveau film(sauvegarde en bd et dans le nas)
async def create_movie(db: Session, data: movieCreate) -> Movie:
    movie = None
    title = data.title
    years = data.release_years
    category = data.category
    infoJson = await search_movie_tmdb(title, years)
    filename = f"{title}{years}"
    img_file_path = await download_image(infoJson["poster_path"], filename)
    torrentXml = await search_movie_torrent(f"{title} {years}")
    torrent, isIntegral, isMulti, lang = await filter_movie_torrent(torrentXml)
    print("RAW LINK =", repr(torrent["link"]))
    if isIntegral and isMulti:
        file_path = await split_movie_download(torrent["link"], filename, title)
        y=0
        for i in file_path:
            y+=1
            movie = Movie(
                title = f"{title} {y}",
                tmdb_id = infoJson["id"],
                description = infoJson["overview"],
                category = category,
                release_date = infoJson["release_date"],
                poster_url = img_file_path,
                updated_at = datetime.date.today()
            )
            db.add(movie)
            db.flush()
            file = File(
                movie_id = movie.id,
                language = EnumLanguage.multi,
                file_path = i
            )
            db.add(file)
        db.commit()
    elif isMulti:
        tmp_file_path = await download_movie_torrent(torrent["link"])
        tmp = max(tmp_file_path, key=lambda p: p.stat().st_size)
        file_path = await transcode_file(tmp, filename)
        movie = Movie(
            title = infoJson["original_title"],
            tmdb_id = infoJson["id"],
            description = infoJson["overview"],
            category = category,
            release_date = infoJson["release_date"],
            poster_url = img_file_path,
            updated_at = datetime.date.today()
        )
        db.add(movie)
        db.flush()
        file = File(
            movie_id = movie.id,
            language = EnumLanguage.multi,
            file_path = file_path
        )
        db.add(file)
        db.commit()
    elif lang == "vf":
        torrent2, isIntegral2, isMulti2, lang2 = await filter_movie_torrent(torrentXml, params="vostfr")
        if lang2 == "vostfr":
            file_path = await merge_movieTrack_download(torrent["link"], torrent2["link"], filename)
            
            movie = Movie(
                title = infoJson["original_title"],
                tmdb_id = infoJson["id"],
                description = infoJson["overview"],
                category = category,
                release_date = infoJson["release_date"],
                poster_url = img_file_path,
                updated_at = datetime.date.today()
            )
            db.add(movie)
            db.flush()
            file = File(
                movie_id = movie.id,
                language = EnumLanguage.multi,
                file_path = file_path
            )
            db.add(file)
            db.commit()
    elif lang == "vostfr":
        torrent2, isIntegral2, isMulti2, lang2 = await filter_movie_torrent(torrentXml, params="vf")
        if lang2 == "vf":
            file_path = await merge_movieTrack_download(torrent["link"], torrent2["link"], filename)
            movie = Movie(
                title = infoJson["original_title"],
                tmdb_id = infoJson["id"],
                description = infoJson["overview"],
                category = category,
                release_date = infoJson["release_date"],
                poster_url = img_file_path,
                updated_at = datetime.date.today()
            )
            db.add(movie)
            db.flush()
            file = File(
                movie_id = movie.id,
                language = EnumLanguage.multi,
                file_path = file_path
            )
            db.add(file)
            db.commit()
    if movie is None:
        raise HTTPException(status_code=404, detail="No Suitable Torrent Found")
    return movie


async def get_all_movie(db: Session) -> list[movieResponce]:
    movies = db.query(Movie).all()
    return [movieResponce.model_validate(m) for m in movies]

async def get_movie_by_id(db : Session, movie_id : int) -> movieResponce:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    return movieResponce.model_validate(movie)

async def get_movie_by_title(db : Session, movie_name : str) -> list[movieResponce]:
    movies = db.query(Movie).filter(Movie.title == movie_name)
    return [movieResponce.model_validate(m) for m in movies]