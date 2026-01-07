import json
import uuid
from shemas.shema_job import JobCreate, JobResponse
from config.redis.redis import redis_client

async def create_job(data:JobCreate) -> JobResponse:
    job_id = str(uuid.uuid4())
    payload = {
        "id": job_id,
        "type": data.type.value,
        "payload": data.payload
    }
    print(f"[API][JOB] creating job {job_id} type={data.type}")
    
    try:
        await redis_client.lpush("jobs", json.dumps(payload))
        print(f"[API][JOB] job {job_id} queued")
    except Exception as e :
        print(f"[API][JOB](ERROR) : {e}")
        raise
    
    return JobResponse(job_id=job_id, status="submitted")