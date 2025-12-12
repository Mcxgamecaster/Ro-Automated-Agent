from __future__ import annotations

import argparse
import logging
from pathlib import Path

import cv2

from .capture import FrameSource
from .config import BotConfig
from .utils import ensure_dir
from .window import find_roblox_window

logger = logging.getLogger(__name__)


def run_calibration(config_path: str, profile: str) -> None:
    cfg = BotConfig.load(config_path)
    hwnd = find_roblox_window(cfg.window_patterns)
    source = FrameSource(hwnd)
    ensure_dir(cfg.debug_dir)
    while True:
        frame = source.grab()
        if frame is None:
            logger.warning("No frame captured; ensure Roblox is running and windowed")
            break
        cv2.imshow("HK3 Calibration", frame)
        key = cv2.waitKey(50)
        if key == ord("q"):
            break
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="HK3 calibration tool")
    parser.add_argument("--config", required=True)
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    run_calibration(args.config, args.profile)


if __name__ == "__main__":
    main()
