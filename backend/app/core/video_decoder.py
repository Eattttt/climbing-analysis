import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from app.config import settings


@dataclass
class VideoMetadata:
    duration_seconds: float = 0.0
    fps: float = 30.0
    width: int = 0
    height: int = 0


@dataclass
class DecodedVideo:
    metadata: VideoMetadata = field(default_factory=VideoMetadata)
    frame_paths: list[str] = field(default_factory=list)
    temp_dir: str = ""


def get_video_metadata(video_path: str) -> VideoMetadata:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)

    video_stream = None
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break

    if not video_stream:
        raise ValueError("未找到视频流")

    fps_str = video_stream.get("r_frame_rate", "30/1")
    num, den = map(int, fps_str.split("/"))
    fps = num / den if den else 30.0

    duration = float(info.get("format", {}).get("duration", 0))

    return VideoMetadata(
        duration_seconds=duration,
        fps=fps,
        width=int(video_stream.get("width", 0)),
        height=int(video_stream.get("height", 0)),
    )


def extract_frames(video_path: str, sample_rate: int = settings.FRAME_SAMPLE_RATE) -> DecodedVideo:
    metadata = get_video_metadata(video_path)
    temp_dir = tempfile.mkdtemp(prefix="climbing_")

    output_pattern = str(Path(temp_dir) / "frame_%06d.jpg")

    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"select=not(mod(n\\,{sample_rate}))",
        "-vsync", "vfr",
        "-q:v", "2",
        "-y",
        output_pattern
    ]
    subprocess.run(cmd, capture_output=True, check=True)

    frame_paths = sorted(str(p) for p in Path(temp_dir).glob("frame_*.jpg"))

    return DecodedVideo(
        metadata=metadata,
        frame_paths=frame_paths,
        temp_dir=temp_dir,
    )


def read_frame(frame_path: str) -> np.ndarray:
    img = cv2.imread(frame_path)
    if img is None:
        raise ValueError(f"无法读取帧: {frame_path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
