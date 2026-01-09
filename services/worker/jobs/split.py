from worker.jobs.base import BaseJob
from worker.services.libtorrent import split_movie_download

class SplitMovieJob(BaseJob):
    async def run(self):
        try:
            payload = self.payload
            url = payload.get("torrent_url_1")
            name = payload.get("filename")
            movie = await split_movie_download(torrent_url=url, filename=name)
        except Exception as e:
            print(f"[WORKER][SPLIT][MOVIE][ERR] : {e}")
            raise