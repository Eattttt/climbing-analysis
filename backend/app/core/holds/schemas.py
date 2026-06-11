from dataclasses import dataclass


@dataclass
class BoundingBox:
    x: float
    y: float
    w: float
    h: float


@dataclass
class HoldResult:
    frame_number: int
    bbox: BoundingBox
    hold_type: str | None
    confidence: float
