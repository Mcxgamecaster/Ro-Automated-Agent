from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def save_json(path: str, data: Any) -> None:
    ensure_dir(str(Path(path).parent))
    Path(path).write_text(json.dumps(data, indent=2, default=str))
    logger.info("Saved %s", path)
