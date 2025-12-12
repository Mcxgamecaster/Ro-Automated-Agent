from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Tuple

from .window import get_client_rect, is_focused

logger = logging.getLogger(__name__)


@dataclass
class SafetyContext:
    hwnd: Optional[int]
    strict_focus: bool
    client_rect: Optional[Tuple[int, int, int, int]]
    max_clicks_per_sec: int = 6
    min_delay_ms: int = 30
    last_action_ts: float = field(default_factory=lambda: 0.0)
    kill_switch: bool = False

    def update_rect(self) -> None:
        if self.hwnd:
            self.client_rect = get_client_rect(self.hwnd)

    def allowed(self) -> bool:
        if self.kill_switch:
            logger.warning("Kill switch active; blocking action")
            return False
        if self.strict_focus and self.hwnd and not is_focused(self.hwnd):
            logger.warning("Roblox window not focused; blocking action")
            return False
        if self.client_rect is None:
            logger.warning("Client rect unknown; blocking action")
            return False
        return True

    def clamp_point(self, x: int, y: int) -> Tuple[int, int]:
        if self.client_rect is None:
            return x, y
        left, top, right, bottom = self.client_rect
        clamped_x = min(max(x, left), right - 1)
        clamped_y = min(max(y, top), bottom - 1)
        return clamped_x, clamped_y

    def rate_limit(self) -> None:
        now = time.time()
        min_delay = self.min_delay_ms / 1000.0
        if now - self.last_action_ts < min_delay:
            time.sleep(min_delay - (now - self.last_action_ts))
        self.last_action_ts = time.time()
