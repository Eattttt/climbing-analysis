import math
from dataclasses import dataclass, field

from app.core.video_decoder import extract_frames, read_frame, DecodedVideo
from app.core.pose.base import PoseEstimator
from app.core.pose.schemas import PoseResult
from app.core.holds.base import HoldDetector
from app.core.holds.schemas import HoldResult
from app.core.reconstruction.geometric_impl import GeometricLifting
from app.core.reconstruction.base import Pose3DResult
from app.core.classification.rule_based import RuleBasedClassifier
from app.core.classification.llm_vision import analyze_movements_with_vision
from app.core.classification.movements import MovementEvent
from app.core.feedback.biomechanics import run_all_rules
from app.core.feedback.claude_coach import generate_coaching


@dataclass
class PipelineContext:
    video_path: str = ""
    decoded: DecodedVideo | None = None
    poses: list[PoseResult] = field(default_factory=list)
    holds: list[HoldResult] = field(default_factory=list)
    poses_3d: list[Pose3DResult] = field(default_factory=list)
    movements: list[MovementEvent] = field(default_factory=list)
    biomechanics_feedback: list[dict] = field(default_factory=list)
    coaching_summary: str = ""
    joint_angle_stats: dict = field(default_factory=dict)


def compute_joint_angles(poses: list[PoseResult]) -> dict:
    joint_timeseries: dict[str, list[float]] = {}

    for pose in poses:
        kps = pose.keypoints
        if len(kps) < 33:
            continue

        def _angle(a, b, c):
            ba = (a.x - b.x, a.y - b.y)
            bc = (c.x - b.x, c.y - b.y)
            dot = ba[0] * bc[0] + ba[1] * bc[1]
            mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
            mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
            if mag_ba * mag_bc == 0:
                return 180.0
            cos_a = max(-1, min(1, dot / (mag_ba * mag_bc)))
            return math.degrees(math.acos(cos_a))

        angles = {
            "left_elbow": _angle(kps[11], kps[13], kps[15]),
            "right_elbow": _angle(kps[12], kps[14], kps[16]),
            "left_knee": _angle(kps[23], kps[25], kps[27]),
            "right_knee": _angle(kps[24], kps[26], kps[28]),
            "left_shoulder": _angle(kps[13], kps[11], kps[23]),
            "right_shoulder": _angle(kps[14], kps[12], kps[24]),
            "left_hip": _angle(kps[11], kps[23], kps[25]),
            "right_hip": _angle(kps[12], kps[24], kps[26]),
        }

        for name, val in angles.items():
            joint_timeseries.setdefault(name, []).append(val)

    stats = {}
    for name, values in joint_timeseries.items():
        if values:
            stats[name] = {
                "min": round(min(values), 1),
                "max": round(max(values), 1),
                "avg": round(sum(values) / len(values), 1),
            }
    return stats


def merge_movements(
    rule_events: list[MovementEvent],
    llm_events: list[MovementEvent],
) -> list[MovementEvent]:
    if not llm_events:
        return rule_events
    if not rule_events:
        return llm_events

    all_events = list(llm_events)

    rule_types = {e.type for e in rule_events}
    llm_types = {e.type for e in llm_events}

    for re in rule_events:
        has_llm_overlap = any(
            abs(re.start_frame - le.start_frame) < 30
            for le in llm_events
            if le.type == re.type
        )
        if not has_llm_overlap:
            all_events.append(re)

    all_events.sort(key=lambda e: e.start_frame)
    return all_events


class ProcessingPipeline:
    def __init__(
        self,
        pose_estimator: PoseEstimator,
        hold_detector: HoldDetector | None = None,
    ):
        self.pose_estimator = pose_estimator
        self.hold_detector = hold_detector
        self.classifier = RuleBasedClassifier()
        self.reconstructor = GeometricLifting()

    async def run(
        self,
        video_path: str,
        sample_rate: int = 5,
        on_stage_change=None,
    ) -> PipelineContext:
        ctx = PipelineContext(video_path=video_path)

        if on_stage_change:
            await on_stage_change("DECODING")

        ctx.decoded = extract_frames(video_path, sample_rate)

        if on_stage_change:
            await on_stage_change("POSE_ESTIMATION")

        for i, frame_path in enumerate(ctx.decoded.frame_paths):
            frame = read_frame(frame_path)
            frame_number = i * sample_rate
            timestamp_ms = frame_number / ctx.decoded.metadata.fps * 1000
            pose = self.pose_estimator.estimate(frame, frame_number, timestamp_ms)
            ctx.poses.append(pose)

        if on_stage_change:
            await on_stage_change("HOLD_DETECTION")

        if self.hold_detector:
            for i, frame_path in enumerate(ctx.decoded.frame_paths):
                frame = read_frame(frame_path)
                frame_number = i * sample_rate
                holds = self.hold_detector.detect(frame, frame_number)
                ctx.holds.extend(holds)

        if on_stage_change:
            await on_stage_change("RECONSTRUCTION_3D")

        ctx.poses_3d = self.reconstructor.lift(ctx.poses)

        if on_stage_change:
            await on_stage_change("CLASSIFYING")

        rule_movements = self.classifier.classify(ctx.poses)

        llm_movements = await analyze_movements_with_vision(
            ctx.decoded.frame_paths,
            ctx.decoded.metadata.fps,
            sample_rate,
        )

        ctx.movements = merge_movements(rule_movements, llm_movements)

        if on_stage_change:
            await on_stage_change("GENERATING_FEEDBACK")

        ctx.biomechanics_feedback = run_all_rules(ctx.poses, ctx.movements)
        ctx.joint_angle_stats = compute_joint_angles(ctx.poses)

        movements_dicts = [
            {
                "type": m.type,
                "start_frame": m.start_frame,
                "end_frame": m.end_frame,
                "confidence": m.confidence,
                "label_cn": m.label_cn,
            }
            for m in ctx.movements
        ]

        ctx.coaching_summary = await generate_coaching(
            duration=ctx.decoded.metadata.duration_seconds,
            movements=movements_dicts,
            biomechanics_feedback=ctx.biomechanics_feedback,
            joint_angle_stats=ctx.joint_angle_stats,
        )

        return ctx
