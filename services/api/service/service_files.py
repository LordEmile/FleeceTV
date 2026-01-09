import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_MEDIA_DIR = Path("/media")
POSTER_DIR = BASE_MEDIA_DIR / "posters"





#download et sauvegarde dans le nas un poster
async def download_image(img_path : str, filename : str):
    url = "https://image.tmdb.org/t/p/w500/"
    request = f"{url}{img_path}"
    file_path = POSTER_DIR / f"{filename}.jpg"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(request)
            response.raise_for_status()
            file_path.write_bytes(response.content)
    except:
        raise HTTPException(status_code=500, detail="DOWNLOAD IMG : failed")
    return str(file_path)

