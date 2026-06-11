import numpy as np

from app.core.holds.base import HoldDetector
from app.core.holds.schemas import HoldResult, BoundingBox


class YOLOHoldDetector(HoldDetector):
    def __init__(self, model_path: str | None = None):
        self.model = None
        if model_path:
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
            except Exception:
                pass

    def detect(self, frame: np.ndarray, frame_number: int) -> list[HoldResult]:
        if self.model is None:
            return []

        results = self.model(frame, verbose=False)
        holds = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                h, w = frame.shape[:2]
                holds.append(HoldResult(
                    frame_number=frame_number,
                    bbox=BoundingBox(
                        x=x1 / w, y=y1 / h,
                        w=(x2 - x1) / w, h=(y2 - y1) / h,
                    ),
                    hold_type=None,
                    confidence=float(box.conf[0]),
                ))
        return holds

    def close(self) -> None:
        self.model = None
