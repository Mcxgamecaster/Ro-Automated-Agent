from __future__ import annotations

import logging
from typing import List, Dict

from ..actions import ActionExecutor

logger = logging.getLogger(__name__)


class LowLevelExecutor:
    def __init__(self, executor: ActionExecutor) -> None:
        self.executor = executor

    def execute(self, actions: List[Dict[str, object]]) -> None:
        for action in actions:
            atype = action.get("type")
            if atype == "click":
                x = int(action["x"])
                y = int(action["y"])
                rect = self.executor.safety.client_rect
                if rect is not None:
                    left, top, _, _ = rect
                    x += left
                    y += top
                self.executor.click(x, y)
            elif atype == "keypress":
                key = str(action.get("key", ""))
                ms_raw = action.get("ms")
                if ms_raw is None:
                    self.executor.press_key(key)
                else:
                    try:
                        self.executor.press_key(key, int(ms_raw))
                    except Exception:  # noqa: BLE001
                        self.executor.press_key(key)
            elif atype == "wait":
                self.executor.wait(int(action.get("ms", 50)))
            else:
                logger.warning("Unknown action type %s", atype)
