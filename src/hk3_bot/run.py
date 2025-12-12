from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import cv2

from .actions import ActionExecutor, kill_switch_listener
from .capture import FrameSource
from .config import BotConfig
from .controller.high_level import LLMPlannerStub, RuleBasedPlanner
from .controller.low_level import LowLevelExecutor
from .controller.policies import PolicyOptions
from .safety import SafetyContext
from .state import GameState
from .utils import ensure_dir, save_json
from .vision.anchors import AnchorDetector
from .window import find_roblox_window, get_client_rect, hwnd_is_valid, is_focused

logger = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Humankind 3 automation runner")
    parser.add_argument("--config", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--assist", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--planner", choices=["rules", "stub"], default="rules")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    logging.basicConfig(level=logging.INFO)
    cfg = BotConfig.load(args.config)
    profile = cfg.profile(args.profile)
    fps = args.fps or profile.fps

    hwnd = find_roblox_window(cfg.window_patterns)
    policy = PolicyOptions(strict_focus=profile.strict_focus, assist_mode=args.assist, debug=args.debug)
    client_rect = get_client_rect(hwnd) if hwnd else None
    gs = GameState(focused=is_focused(hwnd) if hwnd else False, hwnd_valid=bool(hwnd), client_rect=client_rect)

    anchor_detector = AnchorDetector(cfg.templates_dir, cfg.default_scales)
    source = FrameSource(hwnd)
    safety_ctx = SafetyContext(hwnd, policy.strict_focus, client_rect)
    executor = ActionExecutor(safety_ctx)
    low_level = LowLevelExecutor(executor)
    planner = RuleBasedPlanner() if args.planner == "rules" else LLMPlannerStub(cfg.debug_dir)
    listener = kill_switch_listener(executor.safety)

    ensure_dir(cfg.debug_dir)

    delay = 1.0 / max(fps, 1)
    logger.info("Starting main loop at %s FPS", fps)

    while True:
        start = time.time()
        if not hwnd_is_valid(hwnd):
            hwnd = find_roblox_window(cfg.window_patterns)
            safety_ctx.hwnd = hwnd
            source.update_hwnd(hwnd)
        executor.safety.update_rect()
        frame = source.grab()
        if frame is None:
            logger.warning("No frame; exiting loop")
            break
        anchors = anchor_detector.detect_all(frame, profile.anchors)
        gs.anchors = anchors
        gs.focused = is_focused(hwnd) if hwnd else False
        gs.hwnd_valid = hwnd_is_valid(hwnd)
        gs.client_rect = executor.safety.client_rect
        if args.debug:
            debug_path = Path(cfg.debug_dir) / "latest_full.png"
            cv2.imwrite(str(debug_path), frame)
            save_json(str(Path(cfg.debug_dir) / "state.json"), gs.__dict__)
        plan = planner.plan(gs)
        actions = plan.get("actions", [])
        if args.assist and plan.get("requires_confirmation", False):
            resp = input("Assist mode: execute plan? [y/N] ")
            if resp.strip().lower() != "y":
                actions = []
        if not args.dry_run:
            low_level.execute(actions)
        elapsed = time.time() - start
        if delay - elapsed > 0:
            time.sleep(delay - elapsed)

    if listener:
        listener.stop()


if __name__ == "__main__":
    main()
