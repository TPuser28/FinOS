import os
import redis
from rq import Worker, Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
LISTEN_QUEUES = os.getenv("RQ_QUEUES", "ingestion").split(",")

def get_connection():
    return redis.from_url(REDIS_URL)

if __name__ == "__main__":
    conn = get_connection()
    queues = [Queue(name.strip(), connection=conn) for name in LISTEN_QUEUES if name.strip()]
    worker = Worker(queues, connection=conn)
    # with_scheduler=True si tu utilises rq-scheduler
    worker.work(with_scheduler=True)
