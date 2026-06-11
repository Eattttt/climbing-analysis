import subprocess
import tempfile

import cv2
import numpy as np

POSE_CONNECTIONS = [
    (11, 12),  # shoulders
    (11, 13),  # left upper arm
    (13, 15),  # left forearm
    (12, 14),  # right upper arm
    (14, 16),  # right forearm
    (11, 23),  # left torso
    (12, 24),  # right torso
    (23, 24),  # hips
    (23, 25),  # left thigh
    (25, 27),  # left shin
    (24, 26),  # right thigh
    (26, 28),  # right shin
]

COLOR_GREEN = (94, 197, 34)    # #22c55e (BGR)
COLOR_YELLOW = (8, 179, 234)   # #eab308 (BGR)
COLOR_RED = (68, 68, 239)      # #ef4444 (BGR)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

FONT = cv2.FONT_HERSHEY_SIMPLEX


def _visibility_color(visibility: float) -> tuple[int, int, int]:
    if visibility > 0.7:
        return COLOR_GREEN
    if visibility > 0.4:
        return COLOR_YELLOW
    return COLOR_RED


def _find_pose_for_frame(poses: list[dict], frame_number: int) -> dict | None:
    if not poses:
        return None
    best = None
    best_dist = float("inf")
    for p in poses:
        dist = abs(p["frame_number"] - frame_number)
        if dist < best_dist:
            best = p
            best_dist = dist
    if best and best.get("confidence", 0) > 0:
        return best
    return None


def _draw_pose(frame: np.ndarray, pose: dict) -> None:
    h, w = frame.shape[:2]
    kps = pose["landmarks_2d"]

    for i, j in POSE_CONNECTIONS:
        if i >= len(kps) or j >= len(kps):
            continue
        a, b = kps[i], kps[j]
        if a["visibility"] < 0.3 or b["visibility"] < 0.3:
            continue
        avg_vis = (a["visibility"] + b["visibility"]) / 2
        color = _visibility_color(avg_vis)
        pt1 = (int(a["x"] * w), int(a["y"] * h))
        pt2 = (int(b["x"] * w), int(b["y"] * h))
        cv2.line(frame, pt1, pt2, color, 3, cv2.LINE_AA)

    for kp in kps:
        if kp["visibility"] < 0.3:
            continue
        color = COLOR_GREEN if kp["visibility"] > 0.7 else COLOR_YELLOW
        center = (int(kp["x"] * w), int(kp["y"] * h))
        cv2.circle(frame, center, 4, color, -1, cv2.LINE_AA)


def _draw_movement_label(frame: np.ndarray, labels: list[str]) -> None:
    h, w = frame.shape[:2]
    font_scale = max(w, h) / 800.0
    thickness = max(1, int(font_scale * 2))

    y_offset = 20
    for label in labels:
        text = f"[{label}]"
        (tw, th), baseline = cv2.getTextSize(text, FONT, font_scale, thickness)
        x, y = 20, y_offset + th

        overlay = frame.copy()
        cv2.rectangle(overlay, (x - 8, y - th - 8), (x + tw + 8, y + baseline + 8), COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, text, (x, y), FONT, font_scale, COLOR_WHITE, thickness, cv2.LINE_AA)
        y_offset = y + baseline + 16


def _get_active_movements(movements: list[dict], frame_number: int) -> list[str]:
    labels = []
    for m in movements:
        if m["start_frame"] <= frame_number <= m["end_frame"]:
            labels.append(m.get("label_cn", m.get("type", "")))
    return labels


def export_annotated_video(
    video_path: str,
    poses: list[dict],
    movements: list[dict],
    output_path: str | None = None,
) -> str:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"无法打开视频: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", prefix="export_", delete=False)
        output_path = tmp.name
        tmp.close()

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        pose = _find_pose_for_frame(poses, frame_idx)
        if pose:
            _draw_pose(frame, pose)

        labels = _get_active_movements(movements, frame_idx)
        if labels:
            _draw_movement_label(frame, labels)

        proc.stdin.write(frame.tobytes())
        frame_idx += 1

    cap.release()
    proc.stdin.close()
    proc.wait()

    return output_path
