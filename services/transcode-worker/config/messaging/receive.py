import json
import aio_pika
from aio_pika import Message, IncomingMessage
from config.messaging.manage import ManageRabbitMQ
from config.messaging.connect import ConnectRabbitMQ

class EventReceiver:
    def __init__(self, manager: ManageRabbitMQ):
        self.manager = manager

    async def start(self, queue_name: str, routing_key: str, handler):
        channel = await self.manager.connection.get_consume_channel()
        exchange = await self.manager.get_exchange()
        queue = await channel.declare_queue(
            queue_name,
            durable=True
        )
        await queue.bind(exchange=exchange, routing_key=routing_key)
        await queue.consume(lambda message: self.process(message, handler))

    async def process(self, message: IncomingMessage, handler):
        async with message.process():
            payload = json.loads(message.body.decode())
            await handler(payload)
