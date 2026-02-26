from enum import Enum

class EnumWorker(Enum):
    transcode = "pipeline.step.transcode"
    torrent = "pipeline.step.torrent"
    media = "pipeline.step.completed"