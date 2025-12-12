from __future__ import annotations

import importlib
import logging
from typing import Optional, Tuple

import numpy as np

from .window import get_client_rect

logger = logging.getLogger(__name__)


dxcam = importlib.import_module("dxcam") if importlib.util.find_spec("dxcam") else None
mss = importlib.import_module("mss") if importlib.util.find_spec("mss") else None


class FrameSource:
    def __init__(self, hwnd: Optional[int]) -> None:
        self.hwnd = hwnd
        self._dx_camera = dxcam.create(output_color="BGR") if dxcam else None
        self._mss = mss.mss() if mss else None

    def update_hwnd(self, hwnd: Optional[int]) -> None:
        self.hwnd = hwnd

    def grab(self) -> Optional[np.ndarray]:
        rect = get_client_rect(self.hwnd) if self.hwnd else None
        if rect is None:
            return None
        left, top, right, bottom = rect
        width = max(1, right - left)
        height = max(1, bottom - top)
        if self._dx_camera:
            frame = self._dx_camera.grab(region=(left, top, right, bottom))
        elif self._mss:
            monitor = {"left": left, "top": top, "width": width, "height": height}
            frame = np.array(self._mss.grab(monitor))
            frame = frame[:, :, :3][:, :, ::-1]
        else:
            logger.warning("No capture backend available")
            return None
        return frame


def crop_relative(frame: np.ndarray, roi_rel: Tuple[float, float, float, float]) -> np.ndarray:
    h, w = frame.shape[:2]
    x = int(roi_rel[0] * w)
    y = int(roi_rel[1] * h)
    cw = max(1, int(roi_rel[2] * w))
    ch = max(1, int(roi_rel[3] * h))
    return frame[y : y + ch, x : x + cw].copy()


def crop_absolute(frame: np.ndarray, roi_abs: Tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = roi_abs
    return frame[y : y + h, x : x + w].copy()
