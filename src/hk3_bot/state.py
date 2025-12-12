from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class GameState:
    focused: bool
    hwnd_valid: bool
    client_rect: Optional[Tuple[int, int, int, int]]
    timestamp: float = field(default_factory=lambda: time.time())
    mode: str = "unknown"
    anchors: Dict[str, Dict[str, object]] = field(default_factory=dict)
    ui: Dict[str, Dict[str, object]] = field(default_factory=dict)
    numbers: Dict[str, Optional[str]] = field(default_factory=dict)
    debug: Dict[str, object] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, default=str)
