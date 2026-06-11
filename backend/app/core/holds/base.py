from abc import ABC, abstractmethod

import numpy as np

from app.core.holds.schemas import HoldResult


class HoldDetector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray, frame_number: int) -> list[HoldResult]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
