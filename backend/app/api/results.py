from fastapi import APIRouter, HTTPException
from app.database import async_session
from app.models import Video, FramePose, DetectedHold, AnalysisResult
from app.schemas import VideoResultsResponse

router = APIRouter()


@router.get("/api/videos/{video_id}/results", response_model=VideoResultsResponse)
async def get_video_results(video_id: str):
    async with async_session() as session:
        video = await session.get(Video, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = select(Video).where(Video.id == video_id).options(
            selectinload(Video.poses),
            selectinload(Video.holds),
            selectinload(Video.result),
        )
        result = await session.execute(stmt)
        video = result.scalar_one()

        if not video.result:
            raise HTTPException(status_code=400, detail="分析尚未完成")

        return VideoResultsResponse(
            video={
                "id": video.id,
                "filename": video.filename,
                "duration": video.duration_seconds,
                "fps": video.fps,
                "width": video.width,
                "height": video.height,
            },
            poses=[
                {
                    "frame_number": p.frame_number,
                    "timestamp_ms": p.timestamp_ms,
                    "landmarks_2d": p.landmarks_2d,
                    "landmarks_3d": p.landmarks_3d,
                    "confidence": p.confidence,
                }
                for p in video.poses
            ],
            holds=[
                {
                    "frame_number": h.frame_number,
                    "bbox": h.bbox,
                    "hold_type": h.hold_type,
                    "confidence": h.confidence,
                }
                for h in video.holds
            ],
            movements=video.result.movements,
            biomechanics_feedback=video.result.biomechanics_feedback,
            coaching_summary=video.result.coaching_summary,
            joint_angle_stats=video.result.joint_angle_stats,
        )


@router.delete("/api/videos/{video_id}")
async def delete_video(video_id: str):
    async with async_session() as session:
        video = await session.get(Video, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        from app.storage.local import storage
        storage.delete(video.file_path)

        await session.delete(video)
        await session.commit()

        return {"detail": "视频已删除"}
