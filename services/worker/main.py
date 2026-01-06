import asyncio
from worker.workers.consumer import start_worker

def main():
    print("Worker starting...")
    asyncio.run(start_worker())

if __name__ == "__main__":
    main()
