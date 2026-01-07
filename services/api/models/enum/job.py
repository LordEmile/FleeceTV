from enum import Enum
class EnumJob(Enum):
    noop = "noop"
    torrent = "torrent"
    transocde = "transcode"
    merge = "merge"
    delete = "delete"
    scan = "scan"
    