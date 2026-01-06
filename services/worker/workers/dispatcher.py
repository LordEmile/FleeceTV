from worker.jobs.noop import NoopJob

JOB_MAP ={
    "noop": NoopJob
}

async def dispatcher(payload : dict):
    job_type = payload.get("type")
    print(str(job_type))
    if job_type not in JOB_MAP:
        raise ValueError(f"Unknown job type: {job_type}")
    job_class = JOB_MAP[job_type]
    job_instance = job_class(payload)
    print(job_class)
    print(type(job_class))
    await job_instance.run()  