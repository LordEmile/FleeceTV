from pydantic import BaseModel
from shemas.enums.job import EnumJob
from shemas.enums.status import EnumStatus

class PayloadData(BaseModel):
    target: str | None = None
    status: EnumStatus
    expeted_state: EnumStatus | None = None

class CreatePayload(BaseModel):
    step_id: int 
    order_index: int
    job_type: EnumJob
    data: PayloadData
    
    