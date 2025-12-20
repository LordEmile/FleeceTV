import httpx
import tempfile
import asyncio
from html import unescape
from fastapi import HTTPException
from moviepy import VideoFileClip
import libtorrent as libt
from urllib.parse import unquote
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
        raise HTTPException(status_code=500, detail="FFMPEG : failed")


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

#converti un fichier donné en mp4 avec codex unniformisé
async def transcode_file(entry_file:Path, final_name:str | None=None):
    if final_name:
        output_file = entry_file.with_name(f"{final_name}_multi.mp4")
    else:
        output_file = entry_file.with_suffix(".mp4")
    clip = None
    try:
        clip = VideoFileClip(str(entry_file))
        clip.write_videofile(
            str(output_file),
            codec="libx264",
            audio_codec="aac"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TRANCODE : failed :: {str(e)}")
    finally:
        if clip is not None:
            clip.close()
        if entry_file != output_file:
            entry_file.unlink()
    return output_file


#download et sauvegarde en nas une serie de film a partir d'un seul torrent
async def split_movie_download(torrent_url, filename):
    movie_list = await download_movie_torrent(torrent_url)
    path_list = []
    y = 0
    for i in movie_list:
        y += 1
        path = await transcode_file(i, final_name=f"{filename}{y}")
        path_list.append(path)
    if not path_list:
        raise HTTPException(status_code=500, detail="SPLITMOVIE : Failed")
    return path_list
        
#download, sauvegarde en nas et combine plusieur torrent pour en generé un seul fichier
async def merge_movieTrack_download(torrent1_vf, torrent2_vostfr, filename):
    vf_list = await download_movie_torrent(torrent1_vf)
    vostfr_list = await download_movie_torrent(torrent2_vostfr)
    if not vf_list or not vostfr_list:
        raise HTTPException(status_code=404, detail="MERGE: no files downloaded from torrent")
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MERGE : failed ::{str(e)}")
    finally:
        Path(vf_mp4).unlink(missing_ok=True)
        Path(vostfr_mp4).unlink(missing_ok=True)

    


async def normalize_magnet(link: str) -> str:
    if not link:
        raise HTTPException(status_code=400, detail="TORRENT: empty link")

    link = unquote(link.strip())

    if link.startswith("magnet://"):
        link = "magnet:?" + link[len("magnet://"):]

    if link.startswith("magnet:"):
        if "xt=urn:btih:" not in link:
            raise HTTPException(status_code=400, detail="TORRENT: invalid magnet (missing infohash)")
        return link

    raise HTTPException(status_code=400, detail="TORRENT: normalize_magnet received non-magnet link")


def detect_link_type(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("magnet:") or s.startswith("magnet://"):
        return "magnet"
    if s.startswith("http://") or s.startswith("https://"):
        return "torrent_url"
    if s.endswith(".torrent"):
        return "torrent_path"
    return "unknown"


async def fetch_torrent_bytes(url: str) -> bytes:
    url = unescape(url).strip()
    print(f"[TORRENT] GET (no-follow) {url[:140]}")
    async with httpx.AsyncClient(timeout=60, follow_redirects=False) as client:
        r = await client.get(url)
    ct = r.headers.get("content-type", "")
    print(f"[TORRENT] status={r.status_code} content-type={ct}")

    # redirect (souvent vers magnet)
    if r.status_code in (301, 302, 303, 307, 308):
        loc = r.headers.get("Location") or r.headers.get("location")
        if not loc:
            raise HTTPException(status_code=502, detail="TORRENT: redirect without Location position")
        loc = unquote(loc.strip())
        print(f"[TORRENT] redirect -> {loc[:180]}")
        if loc.startswith("magnet://"):
            loc = "magnet:?" + loc[len("magnet://"):]
        if loc.startswith("magnet:"):
            raise HTTPException(status_code=422, detail=f"TORRENT: redirect returned magnet: {loc}")
        return await fetch_torrent_bytes(loc)

    r.raise_for_status()
    data = r.content
    print(f"[TORRENT] bytes={len(data)} first20={data[:20]}")
    # sanity check
    if not data.startswith(b"d"):
        print("[TORRENT][ERR] not bencoded. first200=", data[:200])
        raise HTTPException(status_code=502, detail="TORRENT: response not a .torrent (HTML/error)")

    return data


async def download_movie_torrent(torrent_url: str, timeout_sec: int = 3600) -> list[Path]:
    MOVIE_DIR.mkdir(parents=True, exist_ok=True)
    link = (torrent_url or "").strip()
    link_type = detect_link_type(link)
    print(f"[TORRENT] input type={link_type}")
    print(f"[TORRENT] input preview={link[:180]}")

    #configuration de la session
    session = libt.session()
    session.listen_on(53317, 53317)
    session.start_dht()
    session.add_dht_router("router.bittorrent.com", 6881)
    session.add_dht_router("router.utorrent.com", 6881)
    session.add_dht_router("dht.transmissionbt.com", 6881)
    settings = session.get_settings()
    settings["enable_dht"] = True
    settings["enable_lsd"] = True
    settings["enable_upnp"] = False
    settings["enable_natpmp"] = False
    session.apply_settings(settings)
    try:
        print(f"[TORRENT] dht_state={session.dht_state()}")
    except Exception as e:
        print(f"[TORRENT] dht_state() not available: {e}")

    handle = None
    try:
        atp = {
            "save_path": str(MOVIE_DIR),
            "storage_mode": libt.storage_mode_t.storage_mode_sparse,
        }

        if link_type == "magnet":
            magnet = await normalize_magnet(link)
            print(f"[TORRENT] magnet preview={magnet[:180]}")
            atp["url"] = magnet

        elif link_type == "torrent_url":
            try:
                data = await fetch_torrent_bytes(link)
                ti = libt.torrent_info(libt.bdecode(data))
                print(f"[TORRENT] torrent name={ti.name()}")
                print(f"[TORRENT] files={ti.num_files()} trackers={len(ti.trackers())}")
                for tr in ti.trackers()[:10]:
                    print(f"[TORRENT] tracker: {tr.url}")
                atp["ti"] = ti
            except HTTPException as e:
                #Jackett redirige vers magnet 
                if e.status_code == 422 and "redirect returned magnet" in str(e.detail):
                    magnet = str(e.detail).split("redirect returned magnet:", 1)[-1].strip()
                    magnet = await normalize_magnet(magnet)
                    print(f"[TORRENT] fallback to magnet: {magnet[:180]}")
                    atp["url"] = magnet
                else:
                    raise

        elif link_type == "torrent_path":
            p = Path(link)
            if not p.exists():
                raise HTTPException(status_code=404, detail="TORRENT: .torrent file not found")
            data = p.read_bytes()
            ti = libt.torrent_info(libt.bdecode(data))
            print(f"[TORRENT] torrent(file) name={ti.name()}")
            atp["ti"] = ti

        else:
            raise HTTPException(status_code=400, detail=f"TORRENT: unsupported link type: {link_type}")

        print("[TORRENT] adding torrent to session...")
        handle = session.add_torrent(atp)
        print("[TORRENT] added")
        try:
            handle.force_reannounce()
            handle.force_dht_announce()
        except Exception as e:
            print(f"[TORRENT] force announce not available: {e}")

        # Wait for metadata
        start_meta = asyncio.get_running_loop().time()
        last_print = 0.0
        last_force = 0.0
        while not handle.has_metadata():
            now = asyncio.get_running_loop().time()
            s = handle.status()
            #log
            if now - start_meta > 300:
                print("\n[TORRENT][META TIMEOUT]")
                print(f"  state={s.state} progress={s.progress:.3f}")
                print(f"  peers={s.num_peers} dl={s.download_rate} ul={s.upload_rate}")
                print(f"  error={s.error}")
                try:
                    trs = handle.trackers()
                    print(f"  trackers_count={len(trs)}")
                    for t in trs[:10]:
                        if isinstance(t, dict):
                            print(f"   - {t.get('url')} fail={t.get('fails')} err={t.get('last_error')}")
                        else:
                            print(f"   - {getattr(t, 'url', t)}")
                except Exception as e:
                    print(f"  trackers not available: {e}")
                raise HTTPException(status_code=504, detail="TORRENT: metadata timeout (no peers)")
            if now - last_print >= 5.0:
                print(f"[TORRENT][META] state={s.state} peers={s.num_peers} prog={s.progress:.3f} dl={s.download_rate} ul={s.upload_rate} err={s.error}")
                try:
                    trs = handle.trackers()
                    print(f"[TORRENT][TRACKERS] count={len(trs)}")
                    for t in trs[:5]:
                        if isinstance(t, dict):
                            print(f"  - {t.get('url')} fail={t.get('fails')} err={t.get('last_error')}")
                        else:
                            print(f"  - {getattr(t, 'url', t)}")
                except Exception as e:
                    print(f"[TORRENT][TRACKERS] not available: {e}")
                last_print = now
            # re-force annonce toutes les 30s
            if now - last_force >= 30.0:
                try:
                    handle.force_reannounce()
                    handle.force_dht_announce()
                    print("[TORRENT] forced reannounce + dht_announce")
                except Exception:
                    pass
                last_force = now
            await asyncio.sleep(0.5)
        print("[TORRENT] metadata OK ✅")

        #filtrer les fichier (keep video only)
        fs = handle.get_torrent_info()
        files = fs.files()
        file_count = files.num_files()
        print(f"[TORRENT] file_count={file_count}")
        priorities: list[int] = []
        final_paths: list[Path] = []
        for idx in range(file_count):
            rel = files.file_path(idx)
            name = rel.lower()
            is_movie = name.endswith(".mkv") or name.endswith(".mp4")
            priorities.append(4 if is_movie else 0)
            if is_movie:
                final_paths.append(MOVIE_DIR / rel)
        print(f"[TORRENT] detected movie files={len(final_paths)}")
        if not final_paths:
            raise HTTPException(status_code=404, detail="TORRENT: no .mkv/.mp4 found")
        handle.prioritize_files(priorities)
        print("[TORRENT] priorities set ✅")

        #Download loop
        start = asyncio.get_running_loop().time()
        last_print = 0.0
        while not handle.is_seed():
            s = handle.status()
            if s.error:
                raise HTTPException(status_code=502, detail=f"TORRENT error: {s.error}")
            if asyncio.get_running_loop().time() - start > timeout_sec:
                raise HTTPException(status_code=504, detail="TORRENT: download timeout")
            now = asyncio.get_running_loop().time()
            if now - last_print >= 5.0:
                print(f"[TORRENT][DL] {int(s.progress*100)}% peers={s.num_peers} dl={s.download_rate} ul={s.upload_rate} state={s.state}")
                last_print = now
            await asyncio.sleep(1)
        print("[TORRENT] Téléchargement terminé ✅")
        return final_paths

    finally:
        if handle is not None:
            try:
                session.remove_torrent(handle)
            except Exception as e:
                print(f"[TORRENT] remove_torrent failed: {e}")