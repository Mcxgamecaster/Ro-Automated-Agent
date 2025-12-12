from __future__ import annotations

import importlib
import logging
import re
from typing import Callable, List, Optional, Tuple

from .config import WindowPattern

logger = logging.getLogger(__name__)

win32gui = importlib.import_module("win32gui") if importlib.util.find_spec("win32gui") else None
win32con = importlib.import_module("win32con") if importlib.util.find_spec("win32con") else None


def _matches_pattern(title: str, cls: str, patterns: List[WindowPattern]) -> bool:
    for p in patterns:
        if p.contains and p.contains.lower() in title.lower():
            return True
        if p.regex and re.search(p.regex, title):
            return True
        if p.class_name and p.class_name == cls:
            return True
    return False


def find_roblox_window(patterns: List[WindowPattern]) -> Optional[int]:
    if win32gui is None:
        logger.warning("win32gui not available; cannot find Roblox window")
        return None

    matches: List[int] = []

    def _enum_handler(hwnd: int, _: Callable[[int], None]) -> None:
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        if _matches_pattern(title, cls, patterns):
            matches.append(hwnd)

    win32gui.EnumWindows(_enum_handler, None)
    if not matches:
        return None
    return matches[0]


def get_client_rect(hwnd: int) -> Optional[Tuple[int, int, int, int]]:
    if win32gui is None:
        return None
    try:
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        point = win32gui.ClientToScreen(hwnd, (0, 0))
        return point[0], point[1], point[0] + right, point[1] + bottom
    except Exception:  # noqa: BLE001
        logger.exception("Failed to get client rect")
        return None


def is_focused(hwnd: int) -> bool:
    if win32gui is None or win32con is None:
        return False
    fg = win32gui.GetForegroundWindow()
    return fg == hwnd
