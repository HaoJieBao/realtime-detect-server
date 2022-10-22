import asyncio
from time import sleep

from aiortc import MediaStreamTrack, VideoStreamTrack
from av import VideoFrame
from numpy import ndarray

from .task_queue import task_queue


def funct(frame: ndarray):
    # AI detection
    return frame


class HighlightViolation(VideoStreamTrack):
    kind = "video"

    def __init__(self, track: MediaStreamTrack) -> None:
        super().__init__()
        self.track = track
        self.mode = 0

    def report_success(self, job, connection, result):
        self.mode = 1

    async def recv(self):
        timestamp, video_timestamp_base = await self.next_timestamp()
        frame = await self.track.recv()
        frame = frame.to_ndarray(format="bgr24")

        if len(self.frames) >= 20:
            job = task_queue.enqueue(funct, frame)
            self.frames.clear()

        if self.mode == 0:
            await asyncio.sleep(0.5)

        frame = VideoFrame.from_ndarray(frame, format="bgr24")
        frame.pts = timestamp
        frame.time_base = video_timestamp_base

        return frame
