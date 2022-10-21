import logging
from typing import Any

import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(socketio_server=sio)


logger = logging.getLogger("Signaling")


receiver_id = ""


@sio.event
async def connect(user: str, _: dict[str, Any]):
    logger.info(f"Connected: {user}")
    await sio.emit("receiver", dict(server=receiver_id), to=user)


@sio.event
async def disconnect(user: str):
    logger.info(f"Disconnected: {user}")


@sio.event
async def receiver(user: str):
    global receiver_id
    logger.info(f"receiver is {user}")
    receiver_id = user


@sio.event
async def offer(user: str, payload: dict[str, Any]):
    target = payload["target"]
    offer = payload["offer"]
    logger.info(f"Received an offer from {user} to {target}")
    await sio.emit("offer", dict(source=user, offer=offer), to=target)


@sio.event
async def answer(user: str, payload: dict[str, Any]):
    target = payload["target"]
    answer = payload["answer"]
    logger.info(f"Received an answer from {user} to {target}")
    await sio.emit("answer", dict(source=user, answer=answer), to=target)
