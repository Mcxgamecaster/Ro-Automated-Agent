from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


MatchResult = Dict[str, object]


def multi_scale_match(
    frame: np.ndarray,
    template: np.ndarray,
    scales: List[float],
    threshold: float = 0.8,
) -> MatchResult:
    best: Optional[MatchResult] = None
    for scale in scales:
        resized = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        if frame.shape[0] < resized.shape[0] or frame.shape[1] < resized.shape[1]:
            continue
        res = cv2.matchTemplate(frame, resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if best is None or max_val > best["confidence"]:
            best = {
                "confidence": float(max_val),
                "bbox": (
                    int(max_loc[0]),
                    int(max_loc[1]),
                    int(resized.shape[1]),
                    int(resized.shape[0]),
                ),
                "scale": scale,
                "found": max_val >= threshold,
            }
    if best is None:
        return {"found": False, "confidence": 0.0, "bbox": (0, 0, 0, 0), "scale": 1.0}
    return best
