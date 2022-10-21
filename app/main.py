import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import signaling
from .task_queue import task_queue

app = FastAPI()

app.mount("/ws", signaling.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
