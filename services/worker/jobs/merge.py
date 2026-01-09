from worker.jobs.base import BaseJob
from worker.services.libtorrent import merge_movieTrack_download

class MergeMovieJob(BaseJob):
    async def run(self):
        try:
            payload = self.payload
            url_vf = payload.get("torrent_url_1")
            url_vostfr = payload.get("torrent_url_2")
            name = payload.get("filename")
            movie = await merge_movieTrack_download(torrent1_vf=url_vf, torrent2_vostfr=url_vostfr, filename=name)
        except Exception as e:
            print(f"[WORKER][MERGE][MOVIE][ERR] : {e}")
            raise