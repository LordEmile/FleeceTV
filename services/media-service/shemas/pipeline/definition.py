from pydantic import BaseModel
from models.enums.job import EnumJob
from models.enums.worker import EnumWorker
from typing import List


class StepDefinition(BaseModel):
    worker: EnumWorker
    job_type: EnumJob
    target_path: str | None = None


class PipelineDefinition(BaseModel):
    target_id: int | None = None
    steps: List[StepDefinition]