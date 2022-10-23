import argparse
import asyncio
import logging
import os

import socketio
from aiortc import (
    MediaStreamTrack,
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaRelay

from .highlight_violation import HighlightViolation

# Configurations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Handle AI")

# Global states
sio = socketio.AsyncClient()
pcs: dict[str, RTCPeerConnection] = {}
relay_set: dict[str, RTCPeerConnection] = {}

relay = MediaRelay()
tracks: set[MediaStreamTrack] = set()


@sio.event
async def connect():
    logger.info("handle ai connected")
    await sio.emit("receiver")


@sio.event
async def offer(data: dict):
    offer_dict = data["offer"]
    offer = RTCSessionDescription(sdp=offer_dict["sdp"], type=offer_dict["type"])
    pc = RTCPeerConnection()

    source = data["source"]
    category = data["category"]
    if category == "camera":
        pcs[source] = pc
    elif category == "monitor":
        relay_set[source] = pc
        for track in tracks:
            pc.addTrack(track)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            if category == "camera":
                pcs.pop(source)
            elif category == "monitor":
                relay_set.pop(source)

    @pc.on("track")
    def on_track(track: MediaStreamTrack):
        logger.info("TRACK")
        if track.kind != "video":
            return

        if category == "camera":
            t = HighlightViolation(track)
            tracks.add(t)

            pc.addTrack(relay.subscribe(t))
            for relay_pc in relay_set:
                relay_pc.addTrack(relay.subscribe(t))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await sio.emit(
        "answer",
        dict(
            target=source,
            answer=dict(
                sdp=pc.localDescription.sdp,
                type=pc.localDescription.type,
            ),
        ),
    )


async def main(host: str, port: int):
    await sio.connect(
        f"ws://{host}:{port}",
        transports=["websocket", "polling"],
        socketio_path="/ws/socket.io",
        wait_timeout=60,
    )
    await sio.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", type=str, default="localhost", help="websocket server host"
    )
    parser.add_argument("--port", type=int, default=80, help="websocket server port")
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port))
