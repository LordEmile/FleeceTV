import json
import aio_pika
from aio_pika import Message, DeliveryMode
from config.messaging.manage import ManageRabbitMQ

class EventPublisher:
    def __init__(self, manager: ManageRabbitMQ):
        self.manager = manager

    async def publish(self, routing_key: str, payload: dict):
        exchange  = await self.manager.get_exchange()
        message = Message(
            body=json.dumps(payload).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json"
        )
        await exchange.publish(message=message, routing_key=routing_key)