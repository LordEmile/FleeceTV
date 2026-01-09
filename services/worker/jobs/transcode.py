from worker.jobs.base import BaseJob
from worker.services.ffmpeg import transcode_file
from pathlib import Path

class TranscodeJob(BaseJob):
    async def run(self):
        try:
            payload = self.payload["payload"]
            path = Path(payload.get("filepath"))
            name = payload.get("filename")
            print(f"Starting transcode at {path} || {name}")
            file = await transcode_file(entry_file=path, final_name=name)
        except Exception as e:
            print(f"[WORKER][TRANSCODE][ERR] : {e}")
            raise