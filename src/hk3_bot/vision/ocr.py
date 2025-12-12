from __future__ import annotations

import importlib
import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)

tesseract_spec = importlib.util.find_spec("pytesseract")
pytesseract = importlib.import_module("pytesseract") if tesseract_spec else None


def read_text(img: np.ndarray) -> Optional[str]:
    if pytesseract is None:
        logger.warning("pytesseract not installed; OCR unavailable")
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(thresh, config="--psm 7 --oem 3").strip()
