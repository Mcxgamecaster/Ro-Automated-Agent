from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

from ..config import AnchorTemplate
from .templates import load_template

logger = logging.getLogger(__name__)


class AnchorDetector:
    def __init__(self, templates_dir: str, default_scales: Optional[list] = None) -> None:
        self.templates_dir = templates_dir
        self.default_scales = default_scales or [0.75, 0.85, 1.0, 1.15, 1.3]

    def find_anchor(self, frame, anchor: AnchorTemplate) -> Dict[str, object]:
        from .scaling import multi_scale_match

        template_path = f"{self.templates_dir}/{anchor.file}"
        template = load_template(template_path)
        if template is None:
            return {"found": False, "confidence": 0.0, "bbox": (0, 0, 0, 0), "scale": 1.0}
        result = multi_scale_match(frame, template, anchor.scales or self.default_scales, anchor.threshold)
        return result

    def detect_all(self, frame, anchors: Dict[str, AnchorTemplate]) -> Dict[str, Dict[str, object]]:
        found: Dict[str, Dict[str, object]] = {}
        for name, anchor in anchors.items():
            result = self.find_anchor(frame, anchor)
            if result.get("found"):
                found[name] = result
        return found


def resolve_anchored_roi(
    anchor_bbox: Tuple[int, int, int, int],
    roi_offset: Tuple[int, int],
    roi_size: Tuple[int, int],
    anchor_corner: str,
    client_size: Tuple[int, int],
) -> Tuple[int, int, int, int]:
    ax, ay, aw, ah = anchor_bbox
    dx, dy = roi_offset
    base_x, base_y = ax, ay
    if anchor_corner == "top_right":
        base_x = ax + aw
    elif anchor_corner == "bottom_left":
        base_y = ay + ah
    elif anchor_corner == "bottom_right":
        base_x = ax + aw
        base_y = ay + ah
    x = max(0, min(base_x + dx, client_size[0] - 1))
    y = max(0, min(base_y + dy, client_size[1] - 1))
    w = max(1, min(roi_size[0], client_size[0] - x))
    h = max(1, min(roi_size[1], client_size[1] - y))
    return x, y, w, h
