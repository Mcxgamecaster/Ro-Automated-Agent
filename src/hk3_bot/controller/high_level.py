from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List

from ..state import GameState

logger = logging.getLogger(__name__)


class RuleBasedPlanner:
    def plan(self, state: GameState) -> Dict[str, object]:
        actions: List[Dict[str, object]] = []
        if "CloseX" in state.anchors:
            x, y, w, h = state.anchors["CloseX"]["bbox"]
            actions.append({"type": "click", "x": x + w // 2, "y": y + h // 2, "risky": False})
        return {"intent": "noop", "actions": actions, "requires_confirmation": False}


class LLMPlannerStub:
    def __init__(self, debug_dir: str) -> None:
        self.debug_dir = debug_dir

    def plan(self, state: GameState) -> Dict[str, object]:
        Path(self.debug_dir).mkdir(parents=True, exist_ok=True)
        state_path = Path(self.debug_dir) / "state.json"
        state_path.write_text(state.to_json())
        logger.info("Wrote %s for offline planning", state_path)
        response_path = Path(self.debug_dir) / "planner_response.json"
        if response_path.exists():
            try:
                plan = json.loads(response_path.read_text())
                return plan
            except Exception:  # noqa: BLE001
                logger.exception("Failed to parse planner_response.json")
        return {"intent": "noop", "actions": [], "requires_confirmation": False}
