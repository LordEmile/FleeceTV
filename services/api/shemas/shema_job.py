from pydantic import BaseModel
from models.enum.job import EnumJob

class JobCreate(BaseModel):
    type : EnumJob
    payload : dict

class JobResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None