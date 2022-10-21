import asyncio
import logging

import socketio
from aiortc import (
    MediaStreamTrack,
    RTCDataChannel,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from av import VideoFrame

from .highlight_violation import HighlightViolation
from .task_queue import task_queue

sio = socketio.AsyncClient()
logger = logging.getLogger("Handle AI")

pcs: set[RTCPeerConnection] = set()


@sio.event
async def connect():
    logger.info("handle ai connected")


@sio.event
async def offer(data: dict):
    offer_dict = data["offer"]
    offer = RTCSessionDescription(sdp=offer_dict["sdp"], type=offer_dict["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")

        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track: MediaStreamTrack):
        print("======= received track: ", track)
        if track.kind == "video":
            t = HighlightViolation(track)
            pc.addTrack(t)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    sio.emit("answer", dict(target=data["source"], answer=answer))


async def main():
    await sio.connect(
        "ws://api-server:80",
        transports=["websocket", "polling"],
        socketio_path="/ws/socket.io",
    )
    await sio.wait()


if __name__ == "__main__":
    asyncio.run(main())
