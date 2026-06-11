import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.database import async_session
from app.models import Video, AnalysisResult
from app.schemas import CoachChatRequest
from app.core.feedback.claude_coach import chat_with_coach
from app.core.feedback.prompts import build_coach_message

router = APIRouter()

conversation_store: dict[str, list[dict]] = {}


@router.post("/api/coach/chat")
async def coach_chat(req: CoachChatRequest):
    async with async_session() as session:
        video = await session.get(Video, req.video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")

        from sqlalchemy import select
        stmt = select(AnalysisResult).where(AnalysisResult.video_id == req.video_id)
        result = await session.execute(stmt)
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(status_code=400, detail="分析尚未完成，无法提供教练对话")

    analysis_context = build_coach_message(
        duration=video.duration_seconds,
        movements=analysis.movements,
        biomechanics_feedback=analysis.biomechanics_feedback,
        joint_angle_stats=analysis.joint_angle_stats,
    )

    history = conversation_store.get(req.video_id, [])

    reply = await chat_with_coach(
        video_id=req.video_id,
        user_message=req.message,
        analysis_context=analysis_context,
        history=history,
    )

    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    conversation_store[req.video_id] = history[-20:]

    return {"reply": reply}
