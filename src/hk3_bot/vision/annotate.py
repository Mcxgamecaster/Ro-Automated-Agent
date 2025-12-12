from __future__ import annotations

import cv2
import numpy as np


def draw_bbox(frame: np.ndarray, bbox: tuple, color=(0, 255, 0), label: str = "") -> np.ndarray:
    x, y, w, h = bbox
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    if label:
        cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    return frame
