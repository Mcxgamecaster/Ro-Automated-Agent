from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

if importlib.util.find_spec("yaml"):
    import yaml  # type: ignore
else:
    class _YamlFallback:
        @staticmethod
        def safe_load(data: str) -> dict:
            return json.loads(data)

    yaml = _YamlFallback()  # type: ignore

if importlib.util.find_spec("pydantic"):
    from pydantic import BaseModel, Field, validator
else:
    def Field(default=None, default_factory=None):  # type: ignore
        return default if default is not None else default_factory()

    def validator(*args, **kwargs):  # type: ignore
        def decorator(func):
            return func

        return decorator

    class BaseModel:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            for key, val in kwargs.items():
                setattr(self, key, val)

        def dict(self) -> dict:
            return self.__dict__

        @classmethod
        def parse_obj(cls, obj: dict) -> "BaseModel":
            return cls(**obj)


class RelativeROI(BaseModel):
    x: float
    y: float
    w: float
    h: float

    @validator("x", "y", "w", "h")
    def _clamp(cls, v: float) -> float:  # noqa: N805
        if not 0 <= v <= 1:
            raise ValueError("Relative ROI values must be in 0..1")
        return v

    def to_absolute(self, client_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
        width, height = client_size
        abs_x = int(self.x * width)
        abs_y = int(self.y * height)
        abs_w = max(1, int(self.w * width))
        abs_h = max(1, int(self.h * height))
        return abs_x, abs_y, abs_w, abs_h


class AnchoredROI(BaseModel):
    anchor: str
    offset_px: Tuple[int, int] = Field(default_factory=lambda: (0, 0))
    size_px: Tuple[int, int] = Field(default_factory=lambda: (50, 50))
    anchor_corner: Literal["top_left", "top_right", "bottom_left", "bottom_right"] = "top_left"

    def to_absolute(
        self, anchor_bbox: Tuple[int, int, int, int], client_size: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        ax, ay, aw, ah = anchor_bbox
        dx, dy = self.offset_px
        base_x, base_y = ax, ay
        if self.anchor_corner == "top_right":
            base_x = ax + aw
        elif self.anchor_corner == "bottom_left":
            base_y = ay + ah
        elif self.anchor_corner == "bottom_right":
            base_x = ax + aw
            base_y = ay + ah
        x = max(0, min(base_x + dx, client_size[0] - 1))
        y = max(0, min(base_y + dy, client_size[1] - 1))
        w = max(1, min(self.size_px[0], client_size[0] - x))
        h = max(1, min(self.size_px[1], client_size[1] - y))
        return x, y, w, h


ROIType = Union[RelativeROI, AnchoredROI]


class AnchorTemplate(BaseModel):
    name: str
    file: str
    threshold: float = 0.8
    scales: List[float] = Field(default_factory=lambda: [0.75, 0.85, 1.0, 1.15, 1.3])


class ProfileConfig(BaseModel):
    strict_focus: bool = True
    fps: int = 10
    rois: Dict[str, ROIType] = Field(default_factory=dict)
    anchored_rois: Dict[str, AnchoredROI] = Field(default_factory=dict)
    anchors: Dict[str, AnchorTemplate] = Field(default_factory=dict)
    risky_templates: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    @validator("fps")
    def _positive(cls, v: int) -> int:  # noqa: N805
        if v <= 0:
            raise ValueError("fps must be positive")
        return v


class WindowPattern(BaseModel):
    contains: Optional[str] = None
    regex: Optional[str] = None
    class_name: Optional[str] = None


class BotConfig(BaseModel):
    window_patterns: List[WindowPattern] = Field(default_factory=list)
    profiles: Dict[str, ProfileConfig] = Field(default_factory=dict)
    templates_dir: str = "assets/templates"
    debug_dir: str = "debug"
    logs_dir: str = "logs"
    default_scales: List[float] = Field(default_factory=lambda: [0.75, 0.85, 1.0, 1.15, 1.3])

    @classmethod
    def load(cls, path: Union[str, Path]) -> "BotConfig":
        raw = Path(path).read_text()
        data = yaml.safe_load(raw)
        profiles_data = {}
        for name, payload in data.get("profiles", {}).items():
            rois = {}
            for roi_name, roi_payload in payload.get("rois", {}).items():
                if "anchor" in roi_payload:
                    rois[roi_name] = AnchoredROI(**roi_payload)
                else:
                    rois[roi_name] = RelativeROI(**roi_payload)
            anchors = {}
            for anchor_name, anchor_payload in payload.get("anchors", {}).items():
                anchors[anchor_name] = AnchorTemplate(name=anchor_name, **anchor_payload)
            profiles_data[name] = ProfileConfig(
                strict_focus=payload.get("strict_focus", True),
                fps=payload.get("fps", 10),
                rois=rois,
                anchors=anchors,
                risky_templates=payload.get("risky_templates", []),
            )
        patterns = [WindowPattern(**p) for p in data.get("window_patterns", [])]
        return cls(
            window_patterns=patterns,
            profiles=profiles_data,
            templates_dir=data.get("templates_dir", "assets/templates"),
            debug_dir=data.get("debug_dir", "debug"),
            logs_dir=data.get("logs_dir", "logs"),
            default_scales=data.get("default_scales", [0.75, 0.85, 1.0, 1.15, 1.3]),
        )

    def profile(self, name: str) -> ProfileConfig:
        if name not in self.profiles:
            raise KeyError(f"Profile '{name}' not found in config")
        return self.profiles[name]

    def to_json(self) -> str:
        return json.dumps(self.dict(), indent=2)
