class BaseJob:
    def __init__(self, payload: dict):
        self.payload = payload
        self.job_id = payload.get("id")

    async def run(self):
        raise NotImplementedError
