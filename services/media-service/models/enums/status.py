from enum import Enum

class EnumStatus(Enum):
    PEND = "pending"
    DISP = "dispatched"
    RUN = "running"
    COMP = "completed"
    FAIL = "failed"
