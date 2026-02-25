from sqlalchemy.orm import Session, selectinload
from models.pipeline.step import Step
from models.enums.status import EnumStatus
from models.pipeline.pipeline import Pipeline
from shemas.pipeline.definition import PipelineDefinition
from config.messaging.send import EventPublisher
from shemas.pipeline.payload import CreatePayload, PayloadData

#Fonction creating a new pipeline and its associated steps
async def create_pipeline(db: Session, pipelineDefinition: PipelineDefinition) -> Pipeline:
    pipeline = Pipeline(
        status=EnumStatus.PEND
    )
    db.add(pipeline)
    db.flush()

    for index, i in enumerate(pipelineDefinition.steps):
        step = Step(
            pipeline_id=pipeline.id,
            order_index=index,
            job_type=i.job_type,
            target=i.target_path,
            status=EnumStatus.PEND,
            worker=i.worker
        )
        db.add(step)
    
    db.commit()
    db.refresh(pipeline)
    pipelineWithSteps = (db.query(Pipeline)
                         .options(selectinload(Pipeline.steps))).filter(Pipeline.id == pipeline.id).first()
    return pipelineWithSteps

#Fonction starting a existing pipeline
async def start_pipeline(db: Session, publisher: EventPublisher, pipeline_id: int):
    step: Step = (
        db.query(Step)
        .filter(Step.pipeline_id == pipeline_id, Step.status == EnumStatus.PEND)
        .order_by(Step.order_index.asc()).first()
    )
    payloadData = PayloadData(
        target=step.target,
        status=step.status
    )
    payload = CreatePayload(
        step_id=step.id,
        job_type=step.job_type,
        order_index=step.order_index,
        data=payloadData
    )
    await publisher.publish(
        payload=payload,
        routing_key=step.worker.value
    )

#Fonction retriveing a pipeline and its associated steps
async def get_pipeline(id: int, db: Session):
    pipelineWithSteps = (db.query(Pipeline)
                         .options(selectinload(Pipeline.steps))).filter(Pipeline.id == id).first()
    return pipelineWithSteps


