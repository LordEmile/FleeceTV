import os
import asyncio
from config.messaging.connect import ConnectRabbitMQ
from config.messaging.manage import ManageRabbitMQ
from config.messaging.receive import EventReceiver
from config.messaging.send import EventPublisher

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
connection = ConnectRabbitMQ(url=RABBITMQ_URL)
manager = ManageRabbitMQ(connection=connection)
receiver = EventReceiver(manager=manager)
publisher = EventPublisher(manager=manager)

async def main():
    await connection.connect()
    await manager.setup()
    await receiver.start(
        queue_name="torrent.worker",
        routing_key="pipeline.step.torrent",
        handler=tmp
    )
    print("Torrent worker ready")
    await asyncio.Future()

async def tmp(payload):
    print("Torrent.worker: job done")

if __name__ == "__main__":
    asyncio.run(main())

