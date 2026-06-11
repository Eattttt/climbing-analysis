from app.core.pose.schemas import PoseResult
from app.core.reconstruction.base import Pose3DResult


class GeometricLifting:
    def lift(self, poses: list[PoseResult]) -> list[Pose3DResult]:
        results = []
        for pose in poses:
            kps_3d = []
            for kp in pose.keypoints:
                kps_3d.append({
                    "x": kp.x,
                    "y": kp.y,
                    "z": kp.z,
                    "visibility": kp.visibility,
                })
            results.append(Pose3DResult(
                frame_number=pose.frame_number,
                keypoints_3d=kps_3d,
                confidence=pose.confidence,
            ))
        return results

    def close(self) -> None:
        pass
