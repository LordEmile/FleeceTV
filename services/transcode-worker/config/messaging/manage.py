import aio_pika
from config.messaging.connect import ConnectRabbitMQ
from aio_pika.abc import AbstractRobustExchange

EXCHANGE_NAME = "fleece.events"

class ManageRabbitMQ:
    def __init__(self, connection: ConnectRabbitMQ):
        self.connection = connection
        self.exchange: AbstractRobustExchange | None = None

    async def setup(self):
        channel = await self.connection.get_publish_channel()
        self.exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

    async def get_exchange(self):
        if not self.exchange:
            await self.setup()
        return self.exchange