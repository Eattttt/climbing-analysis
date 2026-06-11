import uuid
import enum
from datetime import datetime

from sqlalchemy import String, Float, Integer, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON

from app.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class VideoStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    DECODING = "DECODING"
    POSE_ESTIMATION = "POSE_ESTIMATION"
    HOLD_DETECTION = "HOLD_DETECTION"
    RECONSTRUCTION_3D = "RECONSTRUCTION_3D"
    CLASSIFYING = "CLASSIFYING"
    GENERATING_FEEDBACK = "GENERATING_FEEDBACK"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


STATUS_PROGRESS = {
    VideoStatus.UPLOADED: 0.0,
    VideoStatus.DECODING: 0.1,
    VideoStatus.POSE_ESTIMATION: 0.25,
    VideoStatus.HOLD_DETECTION: 0.4,
    VideoStatus.RECONSTRUCTION_3D: 0.55,
    VideoStatus.CLASSIFYING: 0.7,
    VideoStatus.GENERATING_FEEDBACK: 0.85,
    VideoStatus.COMPLETED: 1.0,
    VideoStatus.FAILED: 0.0,
}

STATUS_LABELS_CN = {
    VideoStatus.UPLOADED: "已上传",
    VideoStatus.DECODING: "解码中...",
    VideoStatus.POSE_ESTIMATION: "姿态估计中...",
    VideoStatus.HOLD_DETECTION: "岩点检测中...",
    VideoStatus.RECONSTRUCTION_3D: "3D重建中...",
    VideoStatus.CLASSIFYING: "动作分类中...",
    VideoStatus.GENERATING_FEEDBACK: "生成反馈中...",
    VideoStatus.COMPLETED: "分析完成",
    VideoStatus.FAILED: "分析失败",
}


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    fps: Mapped[float] = mapped_column(Float, default=30.0)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[VideoStatus] = mapped_column(SAEnum(VideoStatus), default=VideoStatus.UPLOADED)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    poses: Mapped[list["FramePose"]] = relationship(back_populates="video", cascade="all, delete-orphan")
    holds: Mapped[list["DetectedHold"]] = relationship(back_populates="video", cascade="all, delete-orphan")
    result: Mapped["AnalysisResult | None"] = relationship(back_populates="video", uselist=False, cascade="all, delete-orphan")


class FramePose(Base):
    __tablename__ = "frame_poses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    frame_number: Mapped[int] = mapped_column(Integer)
    timestamp_ms: Mapped[float] = mapped_column(Float)
    landmarks_2d: Mapped[dict] = mapped_column(JSON)
    landmarks_3d: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    video: Mapped["Video"] = relationship(back_populates="poses")


class DetectedHold(Base):
    __tablename__ = "detected_holds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    frame_number: Mapped[int] = mapped_column(Integer)
    bbox: Mapped[dict] = mapped_column(JSON)
    hold_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    video: Mapped["Video"] = relationship(back_populates="holds")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"), unique=True)
    movements: Mapped[list] = mapped_column(JSON, default=list)
    biomechanics_feedback: Mapped[list] = mapped_column(JSON, default=list)
    coaching_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    joint_angle_stats: Mapped[dict] = mapped_column(JSON, default=dict)

    video: Mapped["Video"] = relationship(back_populates="result")
