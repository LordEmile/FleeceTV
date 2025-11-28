import os
import httpx
import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from api.models.movie import Movie
from api.models.files import File
from api.models.enum.language import EnumLanguage
from api.shemas.shema_movie import movieCreate, movieResponce

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_MEDIA_DIR = Path("/media")
POSTER_DIR = BASE_MEDIA_DIR / "posters"
MOVIE_DIR = BASE_MEDIA_DIR / "movies"

#methode pour chercher les information sur un film a partir du titre
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
    

#methode pour créer un film
async def create_movie(db: Session, data: movieCreate) -> Movie:
    title = movieCreate.title
    years = movieCreate.release_years
    category = movieCreate.category
    infoResJson = await search_movie_tmdb(title, years)
    infoJson = infoResJson[0]
    filename = f"{title}{years}"
    img_file_path = await download_image(infoJson["poster_path"], filename)

    movie = Movie(
        title = infoJson["original_title"],
        tmdb_id = infoJson["id"],
        description = infoJson["overview"],
        category = category,
        release_date = infoJson["release_date"],
        poster_url = img_file_path,
        updated_at = datetime.date.today
    )
    file1 = File(
        movie_id = movie.id,
        language = EnumLanguage.vostfr,
        file_path = f"{MOVIE_DIR}/{filename}_vostfr.mp4"
    )
    file2 = File(
        movie_id = movie.id,
        language = EnumLanguage.vf,
        file_path = f"{MOVIE_DIR}/{filename}_vf.mp4"
    )

    db.add(movie)
    db.add(file1)
    db.add(file2)
    db.commit()

    return movie

