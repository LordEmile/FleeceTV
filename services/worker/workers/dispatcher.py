from worker.jobs.noop import NoopJob 
from worker.jobs.torrent import TorrentMovieJob
from worker.jobs.merge import MergeMovieJob
from worker.jobs.split import SplitMovieJob
from worker.jobs.transcode import TranscodeJob

JOB_MAP ={
    "noop": NoopJob,
    "torrentMovie": TorrentMovieJob,
    "mergeMovie": MergeMovieJob,
    "splitMovie": SplitMovieJob,
    "transcode": TranscodeJob
}

async def dispatcher(payload : dict):
    job_type = payload.get("type")
    if job_type not in JOB_MAP:
        raise ValueError(f"Unknown job type: {job_type}")
    
    job_class = JOB_MAP[job_type]
    job_instance = job_class(payload)
    await job_instance.run()  