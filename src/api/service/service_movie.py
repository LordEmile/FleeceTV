import os
import httpx
import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from api.models.movie import Movie
from api.models.files import File
from api.models.enum.language import EnumLanguage
from api.service.service_filter import filter_movie_torrent
from api.shemas.shema_movie import movieCreate, movieResponce

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
JACKETT_KEY = os.getenv("JACKETT_KEY")
BASE_MEDIA_DIR = Path("/media")
POSTER_DIR = BASE_MEDIA_DIR / "posters"
MOVIE_DIR = BASE_MEDIA_DIR / "movies"

#interaction avec tmdb
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
        return response.json()
    
async def download_image(img_path : str, filename :str):
    url = "https://image.tmdb.org/t/p/w500/"
    request = f"{url}{img_path}"
    file_path = POSTER_DIR / f"{filename}.jpg"
    async with httpx.AsyncClient() as client:
        response = await client.get(request)
        response.raise_for_status()
        file_path.write_bytes(response.content)
    return str(file_path)
    

#interaction avec jacket
async def search_movie_torrent(title : str):
    url = ""
    params = {
        "apikey": JACKETT_KEY,
        "t": "movie",
        "q": title,
        "cat": "2000"
    }
    async with httpx.AsyncClient() as client:
        liste = await client.get("url", params=params)
        liste.raise_for_status()
    result = filter_movie_torrent(list=liste)
    torrent = result.link
    return torrent
        
async def download_movie_torrent(magnet : str):
    return


#methode pour créer un film
async def create_movie(db: Session, data: movieCreate) -> Movie:
    title = movieCreate.title
    years = movieCreate.release_years
    category = movieCreate.category
    infoResJson = await search_movie_tmdb(title, years)
    infoJson = infoResJson[0]
    filename = f"{title} {years}"
    img_file_path = await download_image(infoJson["poster_path"], filename)

    torrentXml = await search_movie_torrent(filename)
    torrent, isIntegral, isMulti, lang = await filter_movie_torrent(torrentXml)
    if isIntegral and isMulti:
        #ajouter methode pour separer en plusieur fichier
        file_path = await download_movie_torrent(torrent.link)
    elif isMulti:
        file_path = await download_movie_torrent(torrent.link)
    elif lang == "vf":
        torrent2, isIntegral2, isMulti2, lang2 = await filter_movie_torrent(torrentXml, params="vostfr")
        if lang2 == "vostfr":
            #ajouter methode pour combiner vf vostfr
            file_path = await download_movie_torrent()
    elif lang == "vostfr":
        torrent2, isIntegral2, isMulti2, lang2 = await filter_movie_torrent(torrentXml, params="vf")
        if lang2 == "vf":
            #ajouter methode pour combiner vf vostfr
            file_path = await download_movie_torrent()

    #movie = Movie(
    #    title = infoJson["original_title"],
    #    tmdb_id = infoJson["id"],
    #    description = infoJson["overview"],
    #    category = category,
    #    release_date = infoJson["release_date"],
    #    poster_url = img_file_path,
    #    updated_at = datetime.date.today
    #)
    #file = File(
    #    movie_id = movie.id,
    #    language = EnumLanguage.vostfr,
    #    file_path = f"{MOVIE_DIR}/{filename}_multi"
    #)


    db.add(movie)
    db.add(file)
    db.commit()

    return movie

