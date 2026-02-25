from fastapi import APIRouter, HTTPException, Request, Depends
from models.enums.job import EnumJob
from models.enums.worker import EnumWorker
from sqlalchemy.orm import Session
from config.messaging.send import EventPublisher
from shemas.pipeline.event import CreateEvent, PipelineResponse, StepReponse
from shemas.pipeline.payload import CreatePayload, PayloadData
from shemas.pipeline.definition import PipelineDefinition, StepDefinition
from models.pipeline.pipeline import Pipeline
from services.service_pipeline import create_pipeline, start_pipeline, get_pipeline
from config.db.database import get_pipeline_db

route_job = APIRouter(prefix="/event")

    
@route_job.post("/event",description="Create a new pipeline and initialize its execution" ,status_code=201)
async def create_event(event: CreateEvent, request: Request, db: Session=Depends(get_pipeline_db)) -> PipelineResponse:
    publiser: EventPublisher = request.app.state.publisher
    definition = PipelineDefinition(
        steps=[
            StepDefinition(worker=event.destionnation, job_type=event.job_type, target_path=event.target)
        ]
    )
    pipeline: Pipeline = await create_pipeline(db=db, pipelineDefinition=definition)
    await start_pipeline(db=db, publisher=publiser, pipeline_id=pipeline.id)
    response = PipelineResponse(
        id=pipeline.id,
        status=pipeline.status,
        target_id=pipeline.target_id,
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
        Steps=[
            StepReponse(
                id=step.id,
                job_type=step.job_type,
                status=step.status,
                target=step.target,
                worker=step.worker
            )for step in pipeline.steps
        ]
    )
    return response

@route_job.get("/pipeline/{id}", description="Retrieves the specified pipeline along with all its associated steps and there current status")
async def get_pipeline_state(id: int, db: Session=Depends(get_pipeline_db)) -> PipelineResponse: 
    pipeline = await get_pipeline(id=id, db=db)
    response = PipelineResponse(
        id=pipeline.id,
        status=pipeline.status,
        target_id=pipeline.target_id,
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
        Steps=[
            StepReponse(
                id=step.id,
                job_type=step.job_type,
                status=step.status,
                target=step.target,
                worker=step.worker
            )for step in pipeline.steps
        ]
    )
    return response