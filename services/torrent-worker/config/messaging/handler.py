import asyncio
from config.messaging.send import EventPublisher
from shemas.payload import CreatePayload, PayloadData
from shemas.enums.job import EnumJob
from shemas.enums.status import EnumStatus
from shemas.enums.worker import EnumWorker

async def EventHandler(payload: CreatePayload, publisher: EventPublisher):

    if payload.job_type == EnumJob.NOOP:
        await publish_running(payload=payload, publisher=publisher)
        await asyncio.sleep(3)
        print("noope job: succes")
        await publish_completed(payload=payload, publisher=publisher)
        
    
    elif payload.job_type == EnumJob.TORRENT:
        print("torrent")
    


async def publish_running(payload: CreatePayload, publisher: EventPublisher):
    responseData = PayloadData(
        target=payload.data.target,
        status=EnumStatus.RUN,
        expeted_state=payload.data.status
    ) 
    response = CreatePayload(
        job_type=EnumJob.UPDATE,
        step_id=payload.step_id,
        order_index=payload.order_index,
        data=responseData
    )
    await publisher.publish(
        payload=response,
        routing_key=EnumWorker.media.value
    )


async def publish_completed(payload: CreatePayload, publisher: EventPublisher, final_path: str | None = None):
    responseData = PayloadData(
        target=final_path,
        expeted_state=EnumStatus.RUN,
        status=EnumStatus.COMP
    ) 
    response = CreatePayload(
        job_type=EnumJob.UPDATE,
        step_id=payload.step_id,
        order_index=payload.order_index,
        data=responseData
    )
    await publisher.publish(
        payload=response,
        routing_key=EnumWorker.media.value
    )


async def publish_failed(payload: CreatePayload, publisher: EventPublisher):
    responseData = PayloadData(
        expeted_state=EnumStatus.RUN,
        status=EnumStatus.FAIL
    ) 
    response = CreatePayload(
        job_type=EnumJob.UPDATE,
        step_id=payload.step_id,
        order_index=payload.order_index,
        data=responseData
    )
    await publisher.publish(
        payload=response,
        routing_key=EnumWorker.media.value
    )