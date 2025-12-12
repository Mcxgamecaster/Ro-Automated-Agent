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
                self.executor.click(int(action["x"]), int(action["y"]))
            elif atype == "keypress":
                self.executor.press_key(str(action.get("key", "")))
            elif atype == "wait":
                self.executor.wait(int(action.get("ms", 50)))
            else:
                logger.warning("Unknown action type %s", atype)
