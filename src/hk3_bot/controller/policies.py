from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PolicyOptions:
    strict_focus: bool = True
    assist_mode: bool = False
    debug: bool = False
    planner: str = "rules"
