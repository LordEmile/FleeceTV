import asyncio
import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel

class ConnectRabbitMQ:
    def __init__(self, url: str):
        self.url = url
        self._connection: AbstractRobustConnection | None = None
        self._publish_channel: AbstractRobustChannel | None = None
        self._consume_channel: AbstractRobustChannel | None = None

    async def connect(self):
        backoff = 10
        while True:
            try:
                self._connection = await aio_pika.connect_robust(self.url, heartbeat=30, timeout=10)
                self._publish_channel = await self._connection.channel()
                self._consume_channel = await self._connection.channel()
                break
            except Exception:
                print(f"rabbitMQ not ready, retry in {backoff}")
                await asyncio.sleep(backoff)


    async def close(self):
        if self._connection:
            await self._connection.close()

    async def get_publish_channel(self):
        if not self._connection:
            raise RuntimeError("RabbitMQ not connected")
        channel = self._publish_channel
        return channel
    
    async def get_consume_channel(self):
        if not self._connection:
            raise RuntimeError("RabbitMQ not connected")
        channel = self._consume_channel
        return channel
    
    async def setup(self):
        if not self._connection:
            raise RuntimeError("RabbitMQ not connected")
        channel = self.get_publish_channel()
        

