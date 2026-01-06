import json
from worker.config.redis import redis_client
from worker.config import settings
from worker.workers.dispatcher import dispatcher

async def start_worker():
    print("Worker started, waiting for jobs...")

    while True:
        job = await redis_client.brpop(settings.QUEUE, timeout=5)

        if not job:
            continue

        _, raw = job
        payload = json.loads(raw)
        print(str(payload))

        try:
            await dispatcher(payload)
        except Exception as e:
            print(f"Job failed: {e}")
