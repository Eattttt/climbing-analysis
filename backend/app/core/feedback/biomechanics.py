from app.core.pose.schemas import PoseResult
from app.core.classification.movements import MovementEvent
from app.core.feedback.rules import (
    weight_distribution,
    body_position,
    movement_efficiency,
    grip_analysis,
)


def run_all_rules(
    pose_sequence: list[PoseResult],
    movements: list[MovementEvent] | None = None,
) -> list[dict]:
    feedback = []

    for item in weight_distribution.evaluate(pose_sequence):
        feedback.append({
            "rule": item.rule,
            "severity": item.severity,
            "title": item.title,
            "description": item.description,
            "frames": item.frames,
        })

    for item in body_position.evaluate_elbow_angles(pose_sequence):
        feedback.append({
            "rule": item.rule,
            "severity": item.severity,
            "title": item.title,
            "description": item.description,
            "frames": item.frames,
        })

    for item in body_position.evaluate_hip_position(pose_sequence):
        feedback.append({
            "rule": item.rule,
            "severity": item.severity,
            "title": item.title,
            "description": item.description,
            "frames": item.frames,
        })

    for item in movement_efficiency.evaluate(pose_sequence):
        feedback.append({
            "rule": item.rule,
            "severity": item.severity,
            "title": item.title,
            "description": item.description,
            "frames": item.frames,
        })

    for item in grip_analysis.evaluate(pose_sequence):
        feedback.append({
            "rule": item.rule,
            "severity": item.severity,
            "title": item.title,
            "description": item.description,
            "frames": item.frames,
        })

    return feedback
