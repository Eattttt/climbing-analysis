from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.models import Video, VideoStatus
from app.schemas import VideoUploadResponse
from app.database import async_session
from app.storage.local import storage

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


@router.post("/api/videos/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 '{ext}'，请上传 MP4 或 MOV 文件",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_VIDEO_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大 ({size_mb:.1f}MB)，最大支持 {settings.MAX_VIDEO_SIZE_MB}MB",
        )

    file_path = await storage.save(file.filename, content)

    async with async_session() as session:
        video = Video(
            filename=file.filename,
            file_path=file_path,
            status=VideoStatus.UPLOADED,
        )
        session.add(video)
        await session.commit()
        await session.refresh(video)

        from app.tasks.processor import start_processing
        import asyncio
        asyncio.create_task(start_processing(video.id))

        return VideoUploadResponse(
            video_id=video.id,
            status=video.status.value,
            filename=video.filename,
        )
