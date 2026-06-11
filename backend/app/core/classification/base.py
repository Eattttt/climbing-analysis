from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.pose.schemas import PoseResult
from app.core.classification.movements import MovementEvent


class MovementClassifier(ABC):
    @abstractmethod
    def classify(self, poses: list[PoseResult]) -> list[MovementEvent]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
