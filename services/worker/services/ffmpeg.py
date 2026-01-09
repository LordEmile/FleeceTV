from dotenv import load_dotenv
from pathlib import Path
import json
import shutil
import asyncio

load_dotenv()
BASE_MEDIA_DIR = Path("/media")
MOVIE_DIR = BASE_MEDIA_DIR / "movies"


#fonction pour démarer un service ffmpeg et executer un request
async def run_ffmpeg(cmd: list[str]) -> int:
    print("\nFFMPEG CMD:\n" + " ".join(cmd) + "\n")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    async def pump(stream, prefix: str):
        while True:
            chunk = await stream.read(4096)
            if not chunk:
                break
            text = chunk.decode(errors="ignore").replace("\r", "\n")
            for line in text.splitlines():
                if line.strip():
                    print(f"{prefix}{line}")
    await asyncio.gather(
        pump(proc.stdout, "STDOUT: "),
        pump(proc.stderr, "STDERR: "),
    )
    return await proc.wait()

#fonction pour démarer un service et executer une commande
async def run_cmd(*cmd: str) -> str:
    p = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await p.communicate()
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{err.decode(errors='ignore')}")
    return out.decode(errors="ignore")

#fonction pour obtenir les codecs d'un video
async def probe_codecs(entry_file: Path) -> tuple[str, list[str], list[int]]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise Exception("ffprobe not found")
    vcodec = (await run_cmd(
        ffprobe, "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name",
        "-of", "csv=p=0",
        str(entry_file),
    )).strip()
    acodecs_raw = await run_cmd(
        ffprobe, "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_name",
        "-of", "csv=p=0",
        str(entry_file),
    )
    acodecs = [x.strip() for x in acodecs_raw.splitlines() if x.strip()]
    #return only subrip subs
    subs_json = await run_cmd(
        ffprobe, "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index,codec_name",
        "-of", "json",
        str(entry_file),
    )
    data = json.loads(subs_json or "{}")
    streams = data.get("streams") or []
    scodecs: list[str] = []
    subrip_indexes: list[int] = []
    for s in streams:
        codec = (s.get("codec_name") or "").strip()
        if codec:
            scodecs.append(codec)
        if codec == "subrip" and "index" in s:
            subrip_indexes.append(int(s["index"]))
    return vcodec, acodecs, subrip_indexes

def build_ffmpeg_cmd(
    ffmpeg_bin: str,
    entry_file: Path,
    output_file: Path,
    *,
    vcodec: str,
    acodecs: list[str],
    subrip_indexes: list[int],
    crf: str = "22",
    preset: str = "fast",
    aac_bitrate: str = "384k",
) -> list[str]:
    video_copy = (vcodec == "h264")
    audio_all_aac = (len(acodecs) > 0 and all(a == "aac" for a in acodecs))
    print(f"VIDEO: {vcodec} -> {'copy' if video_copy else 'transcode libx264'}")
    print(f"AUDIO: {acodecs} -> {'copy' if audio_all_aac else 'encode all to AAC'}")
    print(f"SUBS:  {subrip_indexes} -> {'keep subrip' if subrip_indexes else 'none'}")
    cmd = [
        ffmpeg_bin, "-y",
        "-hide_banner", "-loglevel", "info",
        "-i", str(entry_file),
        "-map", "0:v:0?",
        "-map", "0:a?",
        "-movflags", "+faststart",
    ]
    # Subs
    if subrip_indexes:
        for idx in subrip_indexes:
            cmd += ["-map", f"0:{idx}"]
        cmd += ["-c:s", "mov_text"]
    # Video
    if video_copy:
        cmd += ["-c:v", "copy"]
    else:
        cmd += ["-c:v", "libx264", "-crf", crf, "-preset", preset]
    # Audio
    if audio_all_aac:
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "aac", "-b:a", aac_bitrate]
    cmd += [str(output_file)]
    return cmd

#converti un fichier donné en mp4 avec codex unniformisé
async def transcode_file(entry_file:Path, final_name:str | None=None):
    if final_name:
        output_file = entry_file.with_name(f"{final_name}_multi.mp4")
    else:
        output_file = entry_file.with_suffix(".mp4")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise Exception("ffmpeg not found")
    video_codec, audio_codec, subrip_indexes = await probe_codecs(entry_file)
    cmd = build_ffmpeg_cmd(entry_file=entry_file, output_file=output_file, 
                                 acodecs=audio_codec, vcodec=video_codec, subrip_indexes=subrip_indexes,
                                 ffmpeg_bin=ffmpeg)
    try:
        await run_ffmpeg(cmd)
    except Exception as e:
        raise Exception(status_code=500, detail=f"TRANCODE : failed :: {str(e)}")
    if entry_file != output_file:
            entry_file.unlink()
    print("TRANSCODE : Done")
    return output_file