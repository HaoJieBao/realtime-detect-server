import asyncio
import logging

from aiortc import MediaStreamTrack, VideoStreamTrack
from av import VideoFrame
from numpy import ndarray

from .task_queue import task_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Highlight")


def funct(frame: ndarray):
    # AI detection
    return frame


class HighlightViolation(VideoStreamTrack):
    kind = "video"

    def __init__(self, track: MediaStreamTrack) -> None:
        super().__init__()
        self.track = track

    async def recv(self):
        timestamp, video_timestamp_base = await self.next_timestamp()
        frame = await self.track.recv()
        frame = frame.to_ndarray(format="bgr24")
        # job = task_queue.enqueue(funct, frame)
        frame = funct(frame)
        frame = VideoFrame.from_ndarray(frame, format="bgr24")
        frame.pts = timestamp
        frame.time_base = video_timestamp_base

        return frame
