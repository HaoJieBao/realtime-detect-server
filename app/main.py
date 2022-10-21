import time

import redis
from fastapi import FastAPI
from rq import Queue

app = FastAPI()

redis_connection = redis.Redis(host="db", port=6379)
task_queue = Queue(connection=redis_connection)


def do_task(n: str):
    print(f"Working on task {n}")

    time.sleep(0.5)

    print(f"Done task {n}")


@app.get("/")
async def read_index():
    return "The server is active!"


@app.get("/task")
async def add_task(n: str):
    job = task_queue.enqueue(do_task, n)
    queue_length = len(task_queue)
    return f"task {job.id} added to queue at {job.enqueued_at}. {queue_length} tasks in the queue"
