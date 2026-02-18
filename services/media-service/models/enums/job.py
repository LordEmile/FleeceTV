from enum import Enum

class EnumJob(Enum):
    NOOP = "noop"
    TRANSCODE = "transcode"
    TORRENT = "torrent"
    FINDSUB = "findsub"
    UPDATE = "update"
