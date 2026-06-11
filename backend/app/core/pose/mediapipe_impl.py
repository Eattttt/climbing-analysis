import os
import numpy as np
import mediapipe as mp

from app.config import settings
from app.core.pose.base import PoseEstimator
from app.core.pose.schemas import PoseResult, Keypoint

MODEL_FILENAME = "pose_landmarker_heavy.task"


class MediaPipePoseEstimator(PoseEstimator):
    def __init__(self):
        model_path = os.path.join(settings.MODEL_DIR, MODEL_FILENAME)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"MediaPipe 模型文件不存在: {model_path}\n"
                f"请下载 pose_landmarker_heavy.task 到 {settings.MODEL_DIR}"
            )

        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode
        BaseOptions = mp.tasks.BaseOptions

        base_options = BaseOptions(model_asset_path=model_path)
        options = PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False,
        )
        self.landmarker = PoseLandmarker.create_from_options(options)

    def estimate(self, frame: np.ndarray, frame_number: int, timestamp_ms: float) -> PoseResult:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self.landmarker.detect(mp_image)

        if not result.pose_landmarks:
            return PoseResult(
                frame_number=frame_number,
                timestamp_ms=timestamp_ms,
                keypoints=[Keypoint(0, 0, 0, 0) for _ in range(33)],
                confidence=0.0,
            )

        landmarks = result.pose_landmarks[0]
        keypoints = [
            Keypoint(
                x=lm.x,
                y=lm.y,
                z=lm.z,
                visibility=lm.visibility,
            )
            for lm in landmarks
        ]

        avg_confidence = sum(kp.visibility for kp in keypoints) / len(keypoints)

        return PoseResult(
            frame_number=frame_number,
            timestamp_ms=timestamp_ms,
            keypoints=keypoints,
            confidence=avg_confidence,
        )

    def close(self) -> None:
        self.landmarker.close()
