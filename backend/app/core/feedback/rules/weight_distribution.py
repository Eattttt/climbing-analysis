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
    if len(pose_sequence) < 2:
        return []

    offsets = []
    for pose in pose_sequence:
        kps = pose.keypoints
        if len(kps) < 33:
            continue

        l_hip = kps[23]
        r_hip = kps[24]
        l_ankle = kps[27]
        r_ankle = kps[28]

        hip_center_x = (l_hip.x + r_hip.x) / 2
        feet_center_x = (l_ankle.x + r_ankle.x) / 2
        offset = abs(hip_center_x - feet_center_x)
        offsets.append((pose.frame_number, offset))

    if not offsets:
        return []

    avg_offset = sum(o for _, o in offsets) / len(offsets)
    max_offset = max(offsets, key=lambda x: x[1])
    worst_frame = max_offset[0]
    worst_val = max_offset[1]

    if avg_offset < 0.05:
        return [FeedbackItem(
            rule="weight_distribution",
            severity="good",
            title="重心控制良好",
            description="你的重心始终保持在双脚上方，体重分配均匀高效。",
            frames=[offsets[0][0]],
        )]

    severity = "warning" if worst_val < 0.12 else "critical"
    return [FeedbackItem(
        rule="weight_distribution",
        severity=severity,
        title="重心偏移较大",
        description=f"平均重心偏移 {avg_offset:.2f}，最大偏移在第 {worst_frame} 帧（{worst_val:.2f}）。建议保持髋部贴近岩壁，将重心放在双脚上方以减轻手臂负担。",
        frames=[worst_frame],
    )]
