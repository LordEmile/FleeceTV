import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = 0

QUEUE = "jobs"
PROCESSING_QUEUE = "jobs:processing"
FAILED_QUEUE = "jobs:failed"

MAX_RETRY = 3
