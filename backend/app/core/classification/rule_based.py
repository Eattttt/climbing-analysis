import math
from app.core.classification.base import MovementClassifier
from app.core.classification.movements import MovementEvent, MovementType, MOVEMENT_LABELS_CN
from app.core.pose.schemas import PoseResult


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


def _kp_dict(kp) -> dict:
    return {"x": kp.x, "y": kp.y, "z": kp.z}


class RuleBasedClassifier(MovementClassifier):
    def classify(self, poses: list[PoseResult]) -> list[MovementEvent]:
        if len(poses) < 3:
            return []

        events: list[MovementEvent] = []

        for i, pose in enumerate(poses):
            kps = pose.keypoints
            if len(kps) < 33:
                continue

            l_shoulder = _kp_dict(kps[11])
            r_shoulder = _kp_dict(kps[12])
            l_hip = _kp_dict(kps[23])
            r_hip = _kp_dict(kps[24])
            l_knee = _kp_dict(kps[25])
            r_knee = _kp_dict(kps[26])
            l_ankle = _kp_dict(kps[27])
            r_ankle = _kp_dict(kps[28])

            l_knee_angle = _angle(l_hip, l_knee, l_ankle)
            r_knee_angle = _angle(r_hip, r_knee, r_ankle)

            detected_type = MovementType.STATIC

            # --- Cut loose: ankles drop suddenly ---
            if i > 0:
                prev_kps = poses[i - 1].keypoints
                if len(prev_kps) >= 33:
                    prev_ankle_y = (prev_kps[27].y + prev_kps[28].y) / 2
                    curr_ankle_y = (l_ankle["y"] + r_ankle["y"]) / 2
                    if curr_ankle_y - prev_ankle_y > 0.06:
                        detected_type = MovementType.CUT_LOOSE

            # --- Drop knee: knee bent + rotated inward + hip rotation ---
            if detected_type == MovementType.STATIC:
                hip_center_x = (l_hip["x"] + r_hip["x"]) / 2

                # Left drop knee: left knee bent, rotated inward, right leg straighter
                l_knee_inward = abs(l_knee["x"] - hip_center_x) < abs(l_ankle["x"] - hip_center_x)
                l_drop = (
                    l_knee_angle < 100
                    and l_knee_angle < r_knee_angle - 20
                    and l_knee_inward
                    and l_knee["y"] > l_hip["y"] - 0.05
                )

                # Right drop knee
                r_knee_inward = abs(r_knee["x"] - hip_center_x) < abs(r_ankle["x"] - hip_center_x)
                r_drop = (
                    r_knee_angle < 100
                    and r_knee_angle < l_knee_angle - 20
                    and r_knee_inward
                    and r_knee["y"] > r_hip["y"] - 0.05
                )

                if l_drop or r_drop:
                    # Confirm hip rotation (drop knee always rotates hips)
                    shoulder_vec = (r_shoulder["x"] - l_shoulder["x"], r_shoulder["y"] - l_shoulder["y"])
                    hip_vec = (r_hip["x"] - l_hip["x"], r_hip["y"] - l_hip["y"])
                    dot = shoulder_vec[0] * hip_vec[0] + shoulder_vec[1] * hip_vec[1]
                    mag_s = math.sqrt(shoulder_vec[0] ** 2 + shoulder_vec[1] ** 2)
                    mag_h = math.sqrt(hip_vec[0] ** 2 + hip_vec[1] ** 2)
                    if mag_s > 0 and mag_h > 0:
                        cos_a = max(-1, min(1, dot / (mag_s * mag_h)))
                        hip_rotation = math.degrees(math.acos(cos_a))
                    else:
                        hip_rotation = 0
                    if hip_rotation > 8:
                        detected_type = MovementType.DROP_KNEE

            # --- Side body: hip rotation + contralateral hand-foot ---
            if detected_type == MovementType.STATIC:
                l_wrist = _kp_dict(kps[15])
                r_wrist = _kp_dict(kps[16])

                shoulder_vec = (r_shoulder["x"] - l_shoulder["x"], r_shoulder["y"] - l_shoulder["y"])
                hip_vec = (r_hip["x"] - l_hip["x"], r_hip["y"] - l_hip["y"])
                dot = shoulder_vec[0] * hip_vec[0] + shoulder_vec[1] * hip_vec[1]
                mag_s = math.sqrt(shoulder_vec[0] ** 2 + shoulder_vec[1] ** 2)
                mag_h = math.sqrt(hip_vec[0] ** 2 + hip_vec[1] ** 2)
                if mag_s > 0 and mag_h > 0:
                    cos_a = max(-1, min(1, dot / (mag_s * mag_h)))
                    hip_rotation = math.degrees(math.acos(cos_a))
                else:
                    hip_rotation = 0

                l_hand_high = l_wrist["y"] < l_shoulder["y"]
                r_hand_high = r_wrist["y"] < r_shoulder["y"]
                l_foot_low = l_ankle["y"] > l_hip["y"]
                r_foot_low = r_ankle["y"] > r_hip["y"]

                contra_lr = l_hand_high and r_foot_low
                contra_rl = r_hand_high and l_foot_low

                if hip_rotation > 15 and (contra_lr or contra_rl):
                    detected_type = MovementType.SIDE_BODY

            # --- Flag: one leg extended sideways, body rotated ---
            if detected_type == MovementType.STATIC:
                shoulder_width = abs(l_shoulder["x"] - r_shoulder["x"])
                l_leg_span = abs(l_ankle["x"] - l_hip["x"])
                r_leg_span = abs(r_ankle["x"] - r_hip["x"])
                leg_asymmetry = abs(l_leg_span - r_leg_span)

                hip_center_x = (l_hip["x"] + r_hip["x"]) / 2
                shoulder_center_x = (l_shoulder["x"] + r_shoulder["x"]) / 2
                body_rotation = abs(hip_center_x - shoulder_center_x)

                if shoulder_width > 0:
                    normalized_asymmetry = leg_asymmetry / shoulder_width
                    if normalized_asymmetry > 0.6 and body_rotation > 0.03:
                        detected_type = MovementType.FLAG

            if detected_type != MovementType.STATIC:
                events.append(MovementEvent(
                    type=detected_type.value,
                    start_frame=pose.frame_number,
                    end_frame=pose.frame_number,
                    confidence=0.6,
                    label_cn=MOVEMENT_LABELS_CN.get(detected_type, "未知"),
                ))

        return self._merge_events(events)

    def _merge_events(self, events: list[MovementEvent]) -> list[MovementEvent]:
        if not events:
            return []

        merged = [events[0]]
        for evt in events[1:]:
            last = merged[-1]
            if evt.type == last.type and evt.start_frame - last.end_frame <= 5:
                merged[-1] = MovementEvent(
                    type=last.type,
                    start_frame=last.start_frame,
                    end_frame=evt.end_frame,
                    confidence=max(last.confidence, evt.confidence),
                    label_cn=last.label_cn,
                )
            else:
                merged.append(evt)

        return [m for m in merged if m.end_frame - m.start_frame >= 2]

    def close(self) -> None:
        pass
