from pydantic import BaseModel
from models.enums.job import EnumJob
from models.enums.status import EnumStatus

class PayloadData(BaseModel):
    target: str | None = None
    status: EnumStatus

class CreatePayload(BaseModel):
    step_id: int 
    order_index: int
    job_type: EnumJob
    data: PayloadData