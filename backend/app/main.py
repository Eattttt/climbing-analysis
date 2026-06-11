from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db, async_session
from app.models import Video
from app.api import upload, status, results, coach, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="攀岩视频分析系统",
    description="攀岩视频分析、指导、纠正智能体",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(status.router)
app.include_router(results.router)
app.include_router(coach.router)
app.include_router(export.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/videos/{video_id}/file")
async def serve_video_file(video_id: str):
    async with async_session() as session:
        video = await session.get(Video, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

    file_path = Path(video.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=video.filename,
    )
