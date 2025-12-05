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
from api.service.service_files import download_image, download_movie_torrent, merge_movieTrack_download, split_movie_download

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
JACKETT_KEY = os.getenv("JACKETT_KEY")


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
        file_path_list = await split_movie_download(torrent.link)
    elif isMulti:
        file_path = await download_movie_torrent(torrent.link)
    elif lang == "vf":
        torrent2, isIntegral2, isMulti2, lang2 = await filter_movie_torrent(torrentXml, params="vostfr")
        if lang2 == "vostfr":
            file_path = await merge_movieTrack_download(torrent.link, torrent2.link)
    elif lang == "vostfr":
        torrent2, isIntegral2, isMulti2, lang2 = await filter_movie_torrent(torrentXml, params="vf")
        if lang2 == "vf":
            file_path = await merge_movieTrack_download(torrent.link, torrent2.link)

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


    db.add()
    db.add()
    db.commit()

    return 

