import anthropic
from app.config import settings
from app.core.feedback.prompts import COACH_SYSTEM_PROMPT, build_coach_message


def _make_client() -> anthropic.AsyncAnthropic:
    kwargs = {"api_key": settings.ANTHROPIC_API_KEY}
    if settings.ANTHROPIC_BASE_URL:
        kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
    return anthropic.AsyncAnthropic(**kwargs)


async def generate_coaching(
    duration: float,
    movements: list[dict],
    biomechanics_feedback: list[dict],
    joint_angle_stats: dict,
) -> str:
    if not settings.ANTHROPIC_API_KEY:
        return _generate_fallback(biomechanics_feedback)

    client = _make_client()
    user_message = build_coach_message(duration, movements, biomechanics_feedback, joint_angle_stats)

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1500,
            system=COACH_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return _generate_fallback(biomechanics_feedback)
    except Exception as e:
        return _generate_fallback(biomechanics_feedback)


async def chat_with_coach(
    video_id: str,
    user_message: str,
    analysis_context: str,
    history: list[dict] | None = None,
) -> str:
    if not settings.ANTHROPIC_API_KEY:
        return "抱歉，教练对话功能需要配置 API 密钥。请在 .env 文件中设置 ANTHROPIC_API_KEY。"

    client = _make_client()

    messages = [
        {"role": "user", "content": f"以下是视频分析数据：\n\n{analysis_context}"},
        {"role": "assistant", "content": "好的，我已经了解了这段攀岩视频的分析数据。请问你有什么问题？"},
    ]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=800,
            system=COACH_SYSTEM_PROMPT,
            messages=messages,
        )
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return "抱歉，未获得有效回复"
    except Exception as e:
        return f"抱歉，对话出现错误: {str(e)}"


def _generate_fallback(feedback: list[dict]) -> str:
    lines = ["## 攀岩技术分析\n"]

    good = [f for f in feedback if f["severity"] == "good"]
    issues = [f for f in feedback if f["severity"] in ("warning", "critical")]

    if good:
        lines.append("### 做得好的方面")
        for g in good:
            lines.append(f"- {g['title']}: {g['description']}")
        lines.append("")

    if issues:
        lines.append("### 需要改进的方面")
        for iss in issues:
            lines.append(f"- **{iss['title']}**: {iss['description']}")
        lines.append("")

    lines.append("\n> 提示: 配置 ANTHROPIC_API_KEY 可获得更详细的个性化教练指导。")
    return "\n".join(lines)
