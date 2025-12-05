import httpx
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_MEDIA_DIR = Path("/media")
POSTER_DIR = BASE_MEDIA_DIR / "posters"
MOVIE_DIR = BASE_MEDIA_DIR / "movies"


#download le poster de la serie ou du film
async def download_image(img_path : str, filename :str):
    url = "https://image.tmdb.org/t/p/w500/"
    request = f"{url}{img_path}"
    file_path = POSTER_DIR / f"{filename}.jpg"
    async with httpx.AsyncClient() as client:
        response = await client.get(request)
        response.raise_for_status()
        file_path.write_bytes(response.content)
    return str(file_path)


#download movie
async def download_movie_torrent(magnet):
    return

async def split_movie_download(torrent):
    return

async def merge_movieTrack_download(file1, file2):
    return

