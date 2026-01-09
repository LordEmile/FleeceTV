from worker.jobs.base import BaseJob
from worker.services.libtorrent import download_movie_torrent

class TorrentMovieJob(BaseJob):
    async def run(self):
        try:
            payload = self.payload
            url = payload.get("torrent_url_1")
            movie = await download_movie_torrent(torrent_url=url)
        except Exception as e:
            print(f"[WORKER][TORRENT][MOVIE][ERR] : {e}")
            raise