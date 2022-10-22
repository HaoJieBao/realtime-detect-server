import asyncio
import logging

import socketio
from aiortc import (
    MediaStreamTrack,
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaRelay
from av import VideoFrame

from .highlight_violation import HighlightViolation

# Configurations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Handle AI")

# Global states
sio = socketio.AsyncClient()
pcs: set[RTCPeerConnection] = set()
relay_set: set[RTCPeerConnection] = set()

relay = MediaRelay()
tracks: set[MediaStreamTrack] = set()


@sio.event
async def connect():
    logger.info("handle ai connected")


@sio.event
async def offer(data: dict):
    offer_dict = data["offer"]
    category = data["category"]
    offer = RTCSessionDescription(sdp=offer_dict["sdp"], type=offer_dict["type"])
    pc = RTCPeerConnection(
        configuration=RTCConfiguration(
            iceServers=[
                RTCIceServer(urls="stun:stun1.l.google.com:19302"),
                RTCIceServer(urls="stun:stun2.l.google.com:19302"),
                RTCIceServer(urls="stun:stun3.l.google.com:19302"),
                RTCIceServer(urls="stun:stun4.l.google.com:19302"),
            ]
        )
    )

    if category == "camera":
        pcs.add(pc)
    else:
        relay_set.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track: MediaStreamTrack):
        if track.kind == "video":
            if category == "camera":
                t = HighlightViolation(track)
                tracks.add(relay.subscribe(t))
                pc.addTrack(relay.subscribe(t))
                for relay_pc in relay_set:
                    relay_pc.addTrack(relay.subscribe(t))

            else:
                for track in tracks:
                    pc.addTrack(track)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    await sio.emit(
        "answer",
        dict(target=data["source"], answer=dict(sdp=answer.sdp, type=answer.type)),
    )
    return pc


@sio.event
async def connect():
    logger.info("handle ai connected")
    await sio.emit("receiver")


async def main():
    await sio.connect(
        "ws://api-server:80",
        transports=["websocket", "polling"],
        socketio_path="/ws/socket.io",
    )
    await sio.wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
