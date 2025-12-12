from __future__ import annotations

import importlib
import logging
import time
from typing import Optional

from .safety import SafetyContext

keyboard = importlib.import_module("pynput.keyboard") if importlib.util.find_spec("pynput.keyboard") else None
mouse = importlib.import_module("pynput.mouse") if importlib.util.find_spec("pynput.mouse") else None

logger = logging.getLogger(__name__)


class ActionExecutor:
    def __init__(self, safety: SafetyContext) -> None:
        self.safety = safety
        self._keyboard_ctrl = keyboard.Controller() if keyboard else None
        self._mouse_ctrl = mouse.Controller() if mouse else None
        self.click_cooldown = 1.0 / max(self.safety.max_clicks_per_sec, 1)
        self._last_click = 0.0

    def _check(self) -> bool:
        if not self.safety.allowed():
            return False
        self.safety.rate_limit()
        return True

    def press_key(self, key: str, ms: int = 50) -> bool:
        if not self._check() or not self._keyboard_ctrl:
            return False
        self._keyboard_ctrl.press(key)
        time.sleep(ms / 1000.0)
        self._keyboard_ctrl.release(key)
        return True

    def hold_key(self, key: str, on: bool) -> bool:
        if not self._check() or not self._keyboard_ctrl:
            return False
        if on:
            self._keyboard_ctrl.press(key)
        else:
            self._keyboard_ctrl.release(key)
        return True

    def move_mouse(self, dx: int, dy: int) -> bool:
        if not self._check() or not self._mouse_ctrl:
            return False
        self._mouse_ctrl.move(dx, dy)
        return True

    def move_mouse_to(self, x: int, y: int) -> bool:
        if not self._check() or not self._mouse_ctrl:
            return False
        cx, cy = self.safety.clamp_point(x, y)
        self._mouse_ctrl.position = (cx, cy)
        return True

    def click(self, x: int, y: int, button: str = "left") -> bool:
        if not self._check() or not self._mouse_ctrl:
            return False
        now = time.time()
        if now - self._last_click < self.click_cooldown:
            time.sleep(self.click_cooldown - (now - self._last_click))
        cx, cy = self.safety.clamp_point(x, y)
        btn = mouse.Button.left if button == "left" else mouse.Button.right
        self._mouse_ctrl.position = (cx, cy)
        self._mouse_ctrl.click(btn, 1)
        self._last_click = time.time()
        return True

    def type_text(self, text: str) -> bool:
        if not self._check() or not self._keyboard_ctrl:
            return False
        self._keyboard_ctrl.type(text)
        return True

    def wait(self, ms: int) -> bool:
        time.sleep(ms / 1000.0)
        return True

    def set_kill_switch(self, enabled: bool) -> None:
        self.safety.kill_switch = enabled
        if enabled:
            logger.warning("Kill switch engaged")


def kill_switch_listener(context: SafetyContext) -> Optional[object]:
    if keyboard is None:
        return None

    def on_press(key: object) -> None:
        try:
            if key == keyboard.Key.f8:
                context.kill_switch = True
                logger.warning("F8 pressed: kill switch activated")
        except Exception:  # noqa: BLE001
            logger.exception("Kill switch listener error")

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    return listener
