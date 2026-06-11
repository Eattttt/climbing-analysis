import base64
import json
import re
from pathlib import Path

import anthropic
from app.config import settings
from app.core.classification.movements import MovementEvent, MovementType, MOVEMENT_LABELS_CN

VISION_SYSTEM_PROMPT = """你是一位专业的攀岩动作分析专家。你需要通过观察视频帧来识别攀岩者的技术动作。

你需要识别以下动作类型（用英文type返回）：
- flag: 旗式 - 一脚伸出保持平衡，身体不对称
- drop_knee: 折膝 - 膝盖内扣弯曲，髋部内旋，身体围绕膝盖旋转
- dyno: 动态跳跃 - 双脚离墙，动态伸手抓点
- deadpoint: 死点 - 控制性动态移动，一脚保持接触
- campusing: 无脚攀登 - 双脚完全离墙，纯手臂移动
- cut_loose: 脱脚 - 双脚突然脱离岩壁
- rock_over: 翻越 - 重心翻过一只高脚
- barn_door: 开门 - 身体不受控地旋转远离岩壁
- matching: 换手/换脚 - 双手或双脚同时在同一岩点
- stemming: 撑开 - 双脚撑在两面墙上
- knee_bar: 膝盖锁 - 用膝盖夹住岩点固定
- side_body: 侧身 - 髋部转向侧面，异侧手脚配合（如左手高抓+右脚踩点，身体侧转面向左侧）
- rest: 休息 - 单手甩手恢复

注意区分：
- 折膝(drop_knee) ≠ 普通弯曲膝盖。折膝必须有膝盖内扣、髋内旋的特征
- 动态动作需要看到明显的身体位移或腾空
- 旗式需要看到明显的身体不对称和一脚伸出
- 侧身(side_body)的关键特征：(1)髋部明显转向侧面，肩线与髋线不平行 (2)异侧手脚配合，即一侧手在上方抓点，对侧脚在下方踩点 (3)身体朝向与岩壁形成角度。注意侧身≠旗式：旗式是一脚伸出平衡，侧身是髋部旋转+异侧手脚发力

请以JSON数组格式返回，每个元素包含：
- type: 动作类型（英文）
- time_approx: 大约在视频中的秒数
- confidence: 0.0-1.0的置信度
- description: 简短中文描述

只返回JSON数组，不要其他文字。"""


def _encode_frame(frame_path: str) -> dict:
    with open(frame_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": data,
        },
    }


async def analyze_movements_with_vision(
    frame_paths: list[str],
    fps: float,
    sample_rate: int = 5,
) -> list[MovementEvent]:
    if not settings.ANTHROPIC_API_KEY:
        return []

    client = anthropic.AsyncAnthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        **({"base_url": settings.ANTHROPIC_BASE_URL} if settings.ANTHROPIC_BASE_URL else {}),
    )

    frames_per_second = fps / sample_rate
    target_fps = 1
    step = max(1, int(frames_per_second / target_fps))
    sampled_paths = frame_paths[::step]

    if len(sampled_paths) > 16:
        sampled_paths = sampled_paths[:16]

    content = []
    for i, path in enumerate(sampled_paths):
        timestamp = i * step * sample_rate / fps
        content.append(_encode_frame(path))
        content.append({"type": "text", "text": f"帧 {i+1} (约 {timestamp:.1f}秒)"})

    content.append({
        "type": "text",
        "text": "请分析以上攀岩视频帧序列，识别其中的攀岩技术动作。",
    })

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2000,
            system=VISION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                break
        if not text:
            return []
        return _parse_movements(text, fps, sample_rate, step)
    except Exception as e:
        print(f"LLM vision analysis failed: {e}")
        return []


def _parse_movements(
    text: str,
    fps: float,
    sample_rate: int,
    step: int,
) -> list[MovementEvent]:
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if not json_match:
        return []

    try:
        items = json.loads(json_match.group())
    except json.JSONDecodeError:
        return []

    events = []
    valid_types = {t.value for t in MovementType}

    for item in items:
        mtype = item.get("type", "")
        if mtype not in valid_types:
            continue

        time_approx = item.get("time_approx", 0)
        frame_number = int(time_approx * fps / sample_rate) * sample_rate
        confidence = min(1.0, max(0.0, item.get("confidence", 0.5)))

        events.append(MovementEvent(
            type=mtype,
            start_frame=frame_number,
            end_frame=frame_number,
            confidence=confidence,
            label_cn=MOVEMENT_LABELS_CN.get(mtype, item.get("description", mtype)),
        ))

    events.sort(key=lambda e: e.start_frame)
    return _merge_events(events)


def _merge_events(events: list[MovementEvent]) -> list[MovementEvent]:
    if not events:
        return []
    merged = [events[0]]
    for evt in events[1:]:
        last = merged[-1]
        if evt.type == last.type and evt.start_frame - last.end_frame <= 15:
            merged[-1] = MovementEvent(
                type=last.type,
                start_frame=last.start_frame,
                end_frame=evt.end_frame,
                confidence=max(last.confidence, evt.confidence),
                label_cn=last.label_cn,
            )
        else:
            merged.append(evt)
    return merged
