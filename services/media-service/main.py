from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from config.messaging.connect import ConnectRabbitMQ
from config.messaging.manage import ManageRabbitMQ
from config.messaging.receive import EventReceiver
from config.messaging.send import EventPublisher


RABBITMQ_URL = os.getenv("RABBITMQ_URL")
connection = ConnectRabbitMQ(url=RABBITMQ_URL)
manage = ManageRabbitMQ(connection=connection)
receiveComplete = EventReceiver(manager=manage)
receive = EventReceiver(manager=manage)
send = EventPublisher(manager=manage)

async def tmp(payload):
    print("Media-service: job done")

@asynccontextmanager
async def startup(app: FastAPI):
    await connection.connect()
    await manage.setup()
    await receive.start(
        queue_name="media.service",
        routing_key="pipeline.step.completed",
        handler=tmp
    )
    print("Connexion with rabbitMQ establish")
    yield
    print("Connexion with rabbitMQ closed")


app = FastAPI(lifespan=startup)

@app.get("/health")
async def chek_health():
    return{"status":"ok"}