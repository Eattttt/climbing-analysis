from fastapi import APIRouter, HTTPException
from app.database import async_session
from app.models import Video, STATUS_PROGRESS, STATUS_LABELS_CN
from app.schemas import VideoStatusResponse

router = APIRouter()


@router.get("/api/videos/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(video_id: str):
    async with async_session() as session:
        video = await session.get(Video, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        return VideoStatusResponse(
            video_id=video.id,
            status=video.status.value,
            progress=STATUS_PROGRESS.get(video.status, 0.0),
            stage_name=STATUS_LABELS_CN.get(video.status, ""),
            error_message=video.error_message,
        )
