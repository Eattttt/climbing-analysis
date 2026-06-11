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


def _angle(a: dict, b: dict, c: dict) -> float:
    ba = (a["x"] - b["x"], a["y"] - b["y"])
    bc = (c["x"] - b["x"], c["y"] - b["y"])
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
    mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
    if mag_ba * mag_bc == 0:
        return 180.0
    cos_angle = max(-1, min(1, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_angle))


def evaluate_elbow_angles(pose_sequence: list[PoseResult]) -> list[FeedbackItem]:
    if not pose_sequence:
        return []

    bent_frames = []
    for pose in pose_sequence:
        kps = pose.keypoints
        if len(kps) < 33:
            continue

        l_angle = _angle(
            {"x": kps[11].x, "y": kps[11].y},
            {"x": kps[13].x, "y": kps[13].y},
            {"x": kps[15].x, "y": kps[15].y},
        )
        r_angle = _angle(
            {"x": kps[12].x, "y": kps[12].y},
            {"x": kps[14].x, "y": kps[14].y},
            {"x": kps[16].x, "y": kps[16].y},
        )
        avg_angle = (l_angle + r_angle) / 2
        if avg_angle < 90:
            bent_frames.append(pose.frame_number)

    if not bent_frames:
        return [FeedbackItem(
            rule="arm_straightness",
            severity="good",
            title="手臂伸展良好",
            description="你的手臂保持伸直，有效利用骨骼支撑而非肌肉力量。",
            frames=[],
        )]

    ratio = len(bent_frames) / len(pose_sequence)
    if ratio > 0.6:
        return [FeedbackItem(
            rule="arm_straightness",
            severity="critical",
            title="手臂过度弯曲",
            description=f"有 {ratio:.0%} 的时间手臂弯曲超过90°。锁臂会快速消耗前臂力量。尝试伸直手臂，让骨骼承担体重。",
            frames=bent_frames[:3],
        )]
    return [FeedbackItem(
        rule="arm_straightness",
        severity="warning",
        title="手臂偶有弯曲",
        description=f"有 {ratio:.0%} 的时间手臂弯曲超过90°。注意在移动前保持手臂伸直以节省体力。",
        frames=bent_frames[:3],
    )]


def evaluate_hip_position(pose_sequence: list[PoseResult]) -> list[FeedbackItem]:
    if not pose_sequence:
        return []

    far_frames = []
    for pose in pose_sequence:
        kps = pose.keypoints
        if len(kps) < 33:
            continue

        l_shoulder = kps[11]
        r_shoulder = kps[12]
        l_hip = kps[23]
        r_hip = kps[24]

        shoulder_center_y = (l_shoulder.y + r_shoulder.y) / 2
        hip_y = (l_hip.y + r_hip.y) / 2

        if hip_y - shoulder_center_y > 0.15:
            far_frames.append(pose.frame_number)

    if not far_frames:
        return [FeedbackItem(
            rule="hip_position",
            severity="good",
            title="髋部位置良好",
            description="髋部贴近岩壁，重心合理。",
            frames=[],
        )]

    return [FeedbackItem(
        rule="hip_position",
        severity="warning",
        title="髋部远离岩壁",
        description=f"有 {len(far_frames)} 帧髋部明显下坠。保持髋部贴近岩壁可以改善重心位置，减轻手臂负担。",
        frames=far_frames[:3],
    )]
