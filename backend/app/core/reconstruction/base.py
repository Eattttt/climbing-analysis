from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.pose.schemas import PoseResult


@dataclass
class Pose3DResult:
    frame_number: int
    keypoints_3d: list[dict[str, float]]
    confidence: float


class Pose3DEstimator(ABC):
    @abstractmethod
    def lift(self, poses: list[PoseResult]) -> list[Pose3DResult]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
