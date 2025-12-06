import httpx
import tempfile
import asyncio
import libtorrent as libt
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_MEDIA_DIR = Path("/media")
POSTER_DIR = BASE_MEDIA_DIR / "posters"
MOVIE_DIR = BASE_MEDIA_DIR / "movies"


#download et sauvegarde dans le nas un poster
async def download_image(img_path : str, filename :str):
    url = "https://image.tmdb.org/t/p/w500/"
    request = f"{url}{img_path}"
    file_path = POSTER_DIR / f"{filename}.jpg"
    async with httpx.AsyncClient() as client:
        response = await client.get(request)
        response.raise_for_status()
        file_path.write_bytes(response.content)
    return str(file_path)

#converti un fichier donné en mp4 avec codex unniformisé
async def transcode_file(entry_file):
    return


#download et sauvegarde dans le nas un film a partir d'un torrent donné
async def download_movie_torrent(torrent_url):
    session = libt.session()
    session.listen_on(6881, 6891)
    tmp_file = Path(tempfile.gettempdir()) / "tmpMovie.torrent"
    async with httpx.AsyncClient() as client:
        response = await client.get(torrent_url)
        response.raise_for_status()
        tmp_file.write_bytes(response.content)
    info = libt.torrent_info(str(tmp_file))
    params = {
        "save_path": str(MOVIE_DIR),
        "storage_mode": libt.storage_mode_t.storage_mode_sparse,
        "ti": info
    }
    handle = session.add_torrent(params)
    priorities = []
    fs = handle.get_torrent_info()
    file_info = fs.files()
    file_count = file_info.num_files()
    for i in range(file_count):
        file_path = file_info.file_path(i)
        name = file_path.lower()
        is_movie = name.endswith(".mkv") or name.endswith(".mp4")
        if is_movie:
            priorities.append(4)
            final_path = MOVIE_DIR / file_path
        else:
            priorities.append(0)
    handle.prioritize_files(priorities)
    while not handle.is_seed():
        s = handle.status()
        print(f"\r{int(s.progress * 100)}% - Peers: {s.num_peers}", end="")
        await asyncio.sleep(1)
    print("\nTéléchargement terminé")

    return final_path

#download et sauvegarde en nas une serie de film a partir d'un seul torrent
async def split_movie_download(torrent_url):
    return

#download, sauvegarde en nas et combine plusieur torrent pour en generé un seul fichier
async def merge_movieTrack_download(torrent1_url, torrent2_url):
    return

