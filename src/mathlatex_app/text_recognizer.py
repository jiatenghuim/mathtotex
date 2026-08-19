"""Chinese and English OCR wrapper based on Apache-2.0 RapidOCR."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image
from rapidocr import RapidOCR


@dataclass(frozen=True)
class TextRegion:
    text: str
    score: float
    box: tuple[int, int, int, int]

    @property
    def width(self) -> int:
        return self.box[2] - self.box[0]

    @property
    def height(self) -> int:
        return self.box[3] - self.box[1]


class TextRecognizer:
    def __init__(self) -> None:
        self.engine = RapidOCR(params={"Global.log_level": "error"})

    def recognize(self, image: Image.Image) -> list[TextRegion]:
        result = self.engine(image)
        if result.boxes is None or result.txts is None or result.scores is None:
            return []

        regions: list[TextRegion] = []
        for polygon, text, score in zip(result.boxes, result.txts, result.scores):
            points = np.asarray(polygon, dtype=np.float32)
            left = max(0, int(np.floor(points[:, 0].min())))
            top = max(0, int(np.floor(points[:, 1].min())))
            right = min(image.width, int(np.ceil(points[:, 0].max())) + 1)
            bottom = min(image.height, int(np.ceil(points[:, 1].max())) + 1)
            cleaned = str(text).strip()
            if cleaned and right > left and bottom > top:
                regions.append(TextRegion(cleaned, float(score), (left, top, right, bottom)))
        return regions

