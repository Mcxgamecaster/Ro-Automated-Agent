from __future__ import annotations

import importlib
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

cv2 = importlib.import_module("cv2") if importlib.util.find_spec("cv2") else None


@lru_cache(maxsize=64)
def load_template(path: str) -> Optional[object]:
    if cv2 is None:
        logger.warning("cv2 not available; cannot load template %s", path)
        return None
    p = Path(path)
    if not p.exists():
        logger.warning("Template %s not found", path)
        return None
    img = cv2.imread(str(p), cv2.IMREAD_COLOR)
    return img
