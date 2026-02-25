from enum import Enum

class EnumStatus(Enum):
    PEND = "pending"
    RUN = "running"
    COMP = "completed"
    FAIL = "failed"
