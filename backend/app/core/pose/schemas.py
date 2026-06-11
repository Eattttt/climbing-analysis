from dataclasses import dataclass


@dataclass
class Keypoint:
    x: float
    y: float
    z: float
    visibility: float


@dataclass
class PoseResult:
    frame_number: int
    timestamp_ms: float
    keypoints: list[Keypoint]
    confidence: float
