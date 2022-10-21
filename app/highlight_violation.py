from time import sleep

from aiortc import MediaStreamTrack, VideoStreamTrack
from av import VideoFrame
from numpy import ndarray

from .task_queue import task_queue


def funct(arr: ndarray):
    print("hee")
    sleep(0.5)
    return arr


class HighlightViolation(VideoStreamTrack):
    kind = "video"

    def __init__(self, track: MediaStreamTrack) -> None:
        super().__init__()
        self.track = track

    async def recv(self) -> VideoFrame:
        timestamp, video_timestamp_base = await self.next_timestamp()
        frame = await self.track.recv()
        frame = frame.to_ndarray(format="bgr24")
        job = task_queue.enqueue(funct, frame)
        # s = time.time()
        # AI process
        # frame = VideoFrame.from_ndarray(frame, format="bgr24")
        frame.pts = timestamp
        frame.time_base = video_timestamp_base

        return frame
