from worker.jobs.base import BaseJob

class NoopJob(BaseJob):
    async def run(self):
        print("NOOP job executed")