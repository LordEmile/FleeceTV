
from fastapi import APIRouter, HTTPException
from shemas.shema_job import JobCreate, JobResponse
from service.service_job import create_job


route_job = APIRouter(prefix="/job")


@route_job.post("/", response_model=JobResponse)
async def add_job(data:JobCreate):
    try:
        response = await create_job(data)
    except Exception:
        raise HTTPException(status_code=500, detail="Job failed")
    return response