from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from ..state import GameState

logger = logging.getLogger(__name__)


def _normalize_plan(plan: object) -> Dict[str, object]:
    if not isinstance(plan, dict):
        return {"intent": "noop", "actions": [], "requires_confirmation": False}
    intent = str(plan.get("intent", "noop"))
    actions_raw = plan.get("actions", [])
    actions: List[Dict[str, object]] = []
    if isinstance(actions_raw, list):
        for item in actions_raw:
            if not isinstance(item, dict):
                continue
            atype = item.get("type")
            if atype not in {"click", "keypress", "wait"}:
                continue
            action: Dict[str, object] = {"type": atype}
            if atype == "click":
                if "x" in item and "y" in item:
                    try:
                        action["x"] = int(item["x"])
                        action["y"] = int(item["y"])
                    except Exception:  # noqa: BLE001
                        continue
            elif atype == "keypress":
                key = str(item.get("key", ""))
                if not key:
                    continue
                action["key"] = key
                if "ms" in item:
                    try:
                        action["ms"] = int(item["ms"])
                    except Exception:  # noqa: BLE001
                        pass
            elif atype == "wait":
                try:
                    action["ms"] = int(item.get("ms", 50))
                except Exception:  # noqa: BLE001
                    action["ms"] = 50
            risky = bool(item.get("risky", False))
            if risky:
                action["risky"] = True
            actions.append(action)

    requires_confirmation = bool(plan.get("requires_confirmation", False))
    if not requires_confirmation:
        requires_confirmation = any(bool(a.get("risky", False)) for a in actions)

    return {"intent": intent, "actions": actions, "requires_confirmation": requires_confirmation}


class RuleBasedPlanner:
    def plan(self, state: GameState, image_bytes: Optional[bytes] = None) -> Dict[str, object]:
        actions: List[Dict[str, object]] = []
        if "CloseX" in state.anchors:
            x, y, w, h = state.anchors["CloseX"]["bbox"]
            actions.append({"type": "click", "x": x + w // 2, "y": y + h // 2, "risky": False})
        return _normalize_plan({"intent": "noop", "actions": actions, "requires_confirmation": False})


class LLMPlannerStub:
    def __init__(self, debug_dir: str) -> None:
        self.debug_dir = debug_dir

    def plan(self, state: GameState, image_bytes: Optional[bytes] = None) -> Dict[str, object]:
        Path(self.debug_dir).mkdir(parents=True, exist_ok=True)
        state_path = Path(self.debug_dir) / "state.json"
        state_path.write_text(state.to_json())
        logger.info("Wrote %s for offline planning", state_path)
        response_path = Path(self.debug_dir) / "planner_response.json"
        if response_path.exists():
            try:
                plan = json.loads(response_path.read_text())
                return _normalize_plan(plan)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to parse planner_response.json")
        return _normalize_plan({"intent": "noop", "actions": [], "requires_confirmation": False})


class GeminiPlanner:
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        send_vision: bool = True,
        min_interval_s: float = 1.5,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.send_vision = send_vision
        self.min_interval_s = min_interval_s
        self._client = None
        self._api_key = api_key
        self._last_call_ts = 0.0
        self._last_plan: Dict[str, object] = {"intent": "noop", "actions": [], "requires_confirmation": False}

    def _ensure_client(self) -> object:
        if self._client is not None:
            return self._client
        try:
            from google import genai  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("google-genai is not installed. Run: pip install google-genai") from exc

        api_key = self._api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Gemini API key missing. Provide --gemini-api-key or set GEMINI_API_KEY/GOOGLE_API_KEY")
        self._client = genai.Client(api_key=api_key)
        return self._client

    def plan(self, state: GameState, image_bytes: Optional[bytes] = None) -> Dict[str, object]:
        now = time.time()
        if now - self._last_call_ts < self.min_interval_s:
            return _normalize_plan({"intent": "cooldown", "actions": [], "requires_confirmation": False})

        try:
            client = self._ensure_client()
        except Exception:
            logger.exception("GeminiPlanner client initialization failed")
            self._last_plan = _normalize_plan({"intent": "noop", "actions": [], "requires_confirmation": False})
            self._last_call_ts = now
            return self._last_plan

        schema = {
            "type": "object",
            "required": ["intent", "actions", "requires_confirmation"],
            "properties": {
                "intent": {"type": "string"},
                "requires_confirmation": {"type": "boolean"},
                "actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type"],
                        "properties": {
                            "type": {"type": "string", "enum": ["click", "keypress", "wait"]},
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "key": {"type": "string"},
                            "ms": {"type": "integer"},
                            "risky": {"type": "boolean"},
                        },
                        "additionalProperties": True,
                    },
                },
            },
            "additionalProperties": True,
        }

        client_w = None
        client_h = None
        if state.client_rect is not None:
            left, top, right, bottom = state.client_rect
            client_w = max(1, int(right - left))
            client_h = max(1, int(bottom - top))

        size_line = ""
        if client_w is not None and client_h is not None:
            size_line = f"The captured frame size is {client_w}x{client_h} pixels. "

        prompt = (
            "You are the high-level planner for a Windows-only OS input automation bot. "
            "You must output ONLY valid JSON that matches the provided schema. "
            "Do not include markdown. Do not include commentary.\n\n"
            "Rules:\n"
            "- Only use action types: click, keypress, wait\n"
            "- Keep plans short (0-6 actions)\n"
            + size_line
            + "Click coordinates (x,y) must be pixel coordinates relative to the captured frame's top-left (0,0).\n"
            "- Mark risky=true for anything that looks like purchase/spend\n"
            "- If risky actions exist, set requires_confirmation=true\n\n"
            "Here is the current GameState JSON:\n"
            f"{state.to_json()}"
        )

        try:
            from google.genai import types  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("google-genai types import failed") from exc

        contents: list[object] = [prompt]
        if self.send_vision and image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json",
                    response_json_schema=schema,
                ),
            )
        except Exception:  # noqa: BLE001
            logger.exception("Gemini generate_content failed")
            self._last_plan = _normalize_plan({"intent": "noop", "actions": [], "requires_confirmation": False})
            self._last_call_ts = now
            return self._last_plan

        text = getattr(response, "text", None)
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, dict):
            self._last_plan = _normalize_plan(parsed)
            self._last_call_ts = now
            return self._last_plan

        if isinstance(text, str) and text.strip():
            try:
                self._last_plan = _normalize_plan(json.loads(text))
                self._last_call_ts = now
                return self._last_plan
            except Exception:  # noqa: BLE001
                logger.exception("Failed to parse Gemini response as JSON")

        self._last_plan = _normalize_plan({"intent": "noop", "actions": [], "requires_confirmation": False})
        self._last_call_ts = now
        return self._last_plan
