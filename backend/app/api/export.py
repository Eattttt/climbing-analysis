from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import Video, VideoStatus
from app.core.video_export import export_annotated_video

router = APIRouter()


@router.get("/api/videos/{video_id}/export")
async def export_video(video_id: str):
    async with async_session() as session:
        stmt = select(Video).where(Video.id == video_id).options(
            selectinload(Video.poses),
            selectinload(Video.result),
        )
        result = await session.execute(stmt)
        video = result.scalar_one_or_none()

        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        if video.status != VideoStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="视频分析尚未完成")

        if not video.result:
            raise HTTPException(status_code=400, detail="分析结果不存在")

    poses = [
        {
            "frame_number": p.frame_number,
            "landmarks_2d": p.landmarks_2d,
            "confidence": p.confidence,
        }
        for p in video.poses
    ]
    movements = video.result.movements or []

    output_path = export_annotated_video(
        video_path=video.file_path,
        poses=poses,
        movements=movements,
    )

    export_name = f"export_{video.filename}"

    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=export_name,
        background=None,
    )
