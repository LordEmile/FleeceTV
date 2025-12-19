import httpx
import tempfile
import asyncio
from moviepy import VideoFileClip
import libtorrent as libt
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_MEDIA_DIR = Path("/media")
POSTER_DIR = BASE_MEDIA_DIR / "posters"
MOVIE_DIR = BASE_MEDIA_DIR / "movies"

#fonction pour démarer un service ffmpeg et executer un request
async def run_ffmpeg(cmd: list[str]) -> None:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed (code {proc.returncode})\n"
            f"STDOUT:\n{out.decode(errors='ignore')}\n"
            f"STDERR:\n{err.decode(errors='ignore')}"
        )

#download et sauvegarde dans le nas un poster
async def download_image(img_path : str, filename : str):
    url = "https://image.tmdb.org/t/p/w500/"
    request = f"{url}{img_path}"
    file_path = POSTER_DIR / f"{filename}.jpg"
    async with httpx.AsyncClient() as client:
        response = await client.get(request)
        response.raise_for_status()
        file_path.write_bytes(response.content)
    return str(file_path)

#converti un fichier donné en mp4 avec codex unniformisé
async def transcode_file(entry_file:Path, final_name:str | None=None):
    if final_name:
        output_file = entry_file.with_name(f"{final_name}_multi.mp4")
    else:
        output_file = entry_file.with_suffix(".mp4")

    clip = VideoFileClip(str(entry_file))
    clip.write_videofile(
        str(output_file),
        codec="libx264",
        audio_codec="aac"
    )
    clip.close()
    if entry_file != output_file:
        entry_file.unlink()
    return output_file


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
    final_path =[]
    for i in range(file_count):
        file_path = file_info.file_path(i)
        name = file_path.lower()
        is_movie = name.endswith(".mkv") or name.endswith(".mp4")
        if is_movie:
            priorities.append(4)
            path = MOVIE_DIR / file_path
            final_path.append(path)
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
async def split_movie_download(torrent_url, filename):
    movie_list = await download_movie_torrent(torrent_url)
    path_list = []
    y = 0
    for i in movie_list:
        y += 1
        path = await transcode_file(i, final_name=f"{filename}{y}")
        path_list.append(path)
    return path_list
        

#download, sauvegarde en nas et combine plusieur torrent pour en generé un seul fichier
async def merge_movieTrack_download(torrent1_vf, torrent2_vostfr, filename):
    vf_list = await download_movie_torrent(torrent1_vf)
    vostfr_list = await download_movie_torrent(torrent2_vostfr)
    tmp_vf = max(vf_list, key=lambda p: p.stat().st_size)
    tmp_vostfr = max(vostfr_list, key=lambda p: p.stat().st_size)
    vf_mp4 = await transcode_file(tmp_vf, final_name=f"{filename}_VF")
    vostfr_mp4 = await transcode_file(tmp_vostfr, final_name=f"{filename}")

    output_file = Path(vostfr_mp4).with_name(f"{filename}_MULTI.mp4")
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(vostfr_mp4),   # input 0: VOSTFR (vidéo + VO + subs)
            "-i", str(vf_mp4),       # input 1: VF (audio FR)
            "-map", "0:v:0",         # vidéo depuis VOSTFR
            "-map", "1:a:0",         # audio VF depuis VF
            "-map", "0:a:0",         # audio VO depuis VOSTFR
            "-map", "0:s:0?",        # sous-titres FR si présents (le ? évite crash si absent)
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-metadata:s:a:0", "language=fra",
            "-metadata:s:a:0", "title=Français (VF)",
            "-metadata:s:a:1", "language=eng",
            "-metadata:s:a:1", "title=English (VO)",
            "-metadata:s:s:0", "language=fra",
            "-metadata:s:s:0", "title=Sous-titres FR",
            "-disposition:a:0", "default",
            "-disposition:s:0", "0",   # subs OFF par défaut
            str(output_file),
        ]
        await run_ffmpeg(cmd)
        return output_file
    
    finally:
        Path(vf_mp4).unlink(missing_ok=True)
        Path(vostfr_mp4).unlink(missing_ok=True)

    

