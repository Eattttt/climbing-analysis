from dataclasses import dataclass

from app.core.pose.schemas import PoseResult


@dataclass
class FeedbackItem:
    rule: str
    severity: str
    title: str
    description: str
    frames: list[int]


def evaluate(pose_sequence: list[PoseResult]) -> list[FeedbackItem]:
    if len(pose_sequence) < 5:
        return []

    jitter_count = 0
    for i in range(2, len(pose_sequence)):
        prev2 = pose_sequence[i - 2].keypoints
        prev1 = pose_sequence[i - 1].keypoints
        curr = pose_sequence[i].keypoints
        if len(prev2) < 33 or len(prev1) < 33 or len(curr) < 33:
            continue

        for hand_idx in [15, 16]:
            dx1 = prev1[hand_idx].x - prev2[hand_idx].x
            dx2 = curr[hand_idx].x - prev1[hand_idx].x
            if dx1 * dx2 < -0.001:
                jitter_count += 1

    if jitter_count <= 2:
        return [FeedbackItem(
            rule="movement_efficiency",
            severity="good",
            title="动作流畅",
            description="你的手部移动干净利落，没有明显的重复调整。",
            frames=[],
        )]

    severity = "warning" if jitter_count < 10 else "critical"
    return [FeedbackItem(
        rule="movement_efficiency",
        severity=severity,
        title="握点时有重复调整",
        description=f"检测到 {jitter_count} 次手部抖动/重复调整。这会消耗不必要的体力。建议在移动前先看清目标点，一次到位。",
        frames=[],
    )]
