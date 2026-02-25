from pydantic import BaseModel, ConfigDict
from models.enums.worker import EnumWorker
from models.enums.status import EnumStatus
from models.enums.job import EnumJob
from typing import List
import datetime


class CreateEvent(BaseModel):
    destionnation: EnumWorker
    job_type:  EnumJob
    target: str


class StepReponse(BaseModel):
    id: int
    worker: EnumWorker
    job_type: EnumJob
    status: EnumStatus
    target: str | None = None

    model_config = ConfigDict(from_attributes=True)



class PipelineResponse(BaseModel):
    id: int
    target_id: int | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: EnumStatus
    Steps: List[StepReponse]

    model_config = ConfigDict(from_attributes=True)

