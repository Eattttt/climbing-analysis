import math
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
    if not pose_sequence:
        return []

    tension_scores = []
    for pose in pose_sequence:
        kps = pose.keypoints
        if len(kps) < 33:
            continue

        l_shoulder = kps[11]
        r_shoulder = kps[12]
        l_hip = kps[23]
        r_hip = kps[24]

        mid_shoulder_x = (l_shoulder.x + r_shoulder.x) / 2
        mid_shoulder_y = (l_shoulder.y + r_shoulder.y) / 2
        mid_hip_x = (l_hip.x + r_hip.x) / 2
        mid_hip_y = (l_hip.y + r_hip.y) / 2

        dx = mid_hip_x - mid_shoulder_x
        dy = mid_hip_y - mid_shoulder_y
        torso_len = math.sqrt(dx ** 2 + dy ** 2)
        if torso_len > 0:
            sag = abs(dx) / torso_len
            tension_scores.append((pose.frame_number, sag))

    if not tension_scores:
        return []

    avg_sag = sum(s for _, s in tension_scores) / len(tension_scores)

    if avg_sag < 0.1:
        return [FeedbackItem(
            rule="body_tension",
            severity="good",
            title="身体张力良好",
            description="核心收紧，躯干保持稳定。良好的身体张力有助于精确控制。",
            frames=[],
        )]

    severity = "warning" if avg_sag < 0.25 else "critical"
    return [FeedbackItem(
        rule="body_tension",
        severity=severity,
        title="身体张力不足",
        description=f"平均躯干偏移 {avg_sag:.2f}。核心松弛会导致身体摆动，增加手臂负担。建议收紧核心，保持躯干稳定。",
        frames=[tension_scores[0][0]],
    )]
