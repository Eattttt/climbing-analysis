import shutil
from pathlib import Path

from app.database import async_session
from app.models import Video, VideoStatus, FramePose, DetectedHold, AnalysisResult
from app.config import settings
from app.core.pipeline import ProcessingPipeline
from app.core.pose.mediapipe_impl import MediaPipePoseEstimator


async def update_status(video_id: str, status: VideoStatus):
    async with async_session() as session:
        video = await session.get(Video, video_id)
        if video:
            video.status = status
            await session.commit()


async def mark_failed(video_id: str, error: str):
    async with async_session() as session:
        video = await session.get(Video, video_id)
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = error
            await session.commit()


async def start_processing(video_id: str):
    try:
        async with async_session() as session:
            video = await session.get(Video, video_id)
            if not video:
                return
            video_path = video.file_path

        pose_estimator = MediaPipePoseEstimator()

        pipeline = ProcessingPipeline(pose_estimator=pose_estimator)

        ctx = await pipeline.run(
            video_path=video_path,
            sample_rate=settings.FRAME_SAMPLE_RATE,
            on_stage_change=lambda s: update_status(video_id, VideoStatus(s)),
        )

        async with async_session() as session:
            video = await session.get(Video, video_id)
            if not video:
                return

            video.duration_seconds = ctx.decoded.metadata.duration_seconds
            video.fps = ctx.decoded.metadata.fps
            video.width = ctx.decoded.metadata.width
            video.height = ctx.decoded.metadata.height

            for pose in ctx.poses:
                fp = FramePose(
                    video_id=video_id,
                    frame_number=pose.frame_number,
                    timestamp_ms=pose.timestamp_ms,
                    landmarks_2d=[{"x": kp.x, "y": kp.y, "z": kp.z, "visibility": kp.visibility} for kp in pose.keypoints],
                    confidence=pose.confidence,
                )
                session.add(fp)

            for i, pose3d in enumerate(ctx.poses_3d):
                if i < len(ctx.poses):
                    pass

            for hold in ctx.holds:
                dh = DetectedHold(
                    video_id=video_id,
                    frame_number=hold.frame_number,
                    bbox={"x": hold.bbox.x, "y": hold.bbox.y, "w": hold.bbox.w, "h": hold.bbox.h},
                    hold_type=hold.hold_type,
                    confidence=hold.confidence,
                )
                session.add(dh)

            result = AnalysisResult(
                video_id=video_id,
                movements=[
                    {"type": m.type, "start_frame": m.start_frame, "end_frame": m.end_frame, "confidence": m.confidence, "label_cn": m.label_cn}
                    for m in ctx.movements
                ],
                biomechanics_feedback=ctx.biomechanics_feedback,
                coaching_summary=ctx.coaching_summary,
                joint_angle_stats=ctx.joint_angle_stats,
            )
            session.add(result)

            video.status = VideoStatus.COMPLETED
            await session.commit()

        pose_estimator.close()

        temp_dir = ctx.decoded.temp_dir
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        await mark_failed(video_id, str(e))
