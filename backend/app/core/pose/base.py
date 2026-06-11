from abc import ABC, abstractmethod

import numpy as np

from app.core.pose.schemas import PoseResult


class PoseEstimator(ABC):
    @abstractmethod
    def estimate(self, frame: np.ndarray, frame_number: int, timestamp_ms: float) -> PoseResult:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
