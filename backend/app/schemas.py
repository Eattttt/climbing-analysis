from pydantic import BaseModel
from typing import Any


class VideoUploadResponse(BaseModel):
    video_id: str
    status: str
    filename: str


class VideoStatusResponse(BaseModel):
    video_id: str
    status: str
    progress: float
    stage_name: str
    error_message: str | None = None


class Keypoint2D(BaseModel):
    x: float
    y: float
    z: float
    visibility: float


class PoseFrameResult(BaseModel):
    frame_number: int
    timestamp_ms: float
    landmarks_2d: list[Keypoint2D]
    landmarks_3d: list[dict[str, float]] | None = None
    confidence: float


class HoldResult(BaseModel):
    frame_number: int
    bbox: dict[str, float]
    hold_type: str | None = None
    confidence: float


class MovementEvent(BaseModel):
    type: str
    start_frame: int
    end_frame: int
    confidence: float
    label_cn: str


class BiomechanicsFeedbackItem(BaseModel):
    rule: str
    severity: str
    title: str
    description: str
    frames: list[int]


class JointAngleStat(BaseModel):
    min: float
    max: float
    avg: float


class VideoResultsResponse(BaseModel):
    video: dict[str, Any]
    poses: list[PoseFrameResult]
    holds: list[HoldResult]
    movements: list[MovementEvent]
    biomechanics_feedback: list[BiomechanicsFeedbackItem]
    coaching_summary: str | None = None
    joint_angle_stats: dict[str, JointAngleStat]


class CoachChatRequest(BaseModel):
    video_id: str
    message: str


class CoachChatResponse(BaseModel):
    reply: str


class ErrorResponse(BaseModel):
    detail: str
    code: str = "ERROR"
