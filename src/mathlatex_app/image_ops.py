"""Small, dependency-light image preprocessing helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps


@dataclass(frozen=True)
class FormulaRegion:
    image: Image.Image
    box: tuple[int, int, int, int]


def light_background(image: Image.Image) -> Image.Image:
    """Normalize screenshots so the recognizer always sees dark ink on white."""
    rgb = image.convert("RGB")
    if float(np.median(np.asarray(ImageOps.grayscale(rgb)))) < 127:
        return ImageOps.invert(rgb)
    return rgb


def trim_background(image: Image.Image, *, threshold: int = 245) -> Image.Image:
    """Crop uniform light margins while keeping a small safety border."""
    rgb = light_background(image)
    gray = np.asarray(ImageOps.grayscale(rgb))
    ink = gray < threshold
    if not ink.any():
        return rgb

    rows, cols = np.where(ink)
    left = max(0, int(cols.min()) - 6)
    top = max(0, int(rows.min()) - 6)
    right = min(rgb.width, int(cols.max()) + 7)
    bottom = min(rgb.height, int(rows.max()) + 7)
    return rgb.crop((left, top, right, bottom))


def split_formula_lines(
    image: Image.Image,
    *,
    threshold: int = 235,
    min_ink_pixels: int = 3,
    merge_gap: int = 12,
) -> list[FormulaRegion]:
    """Split a light-background screenshot into horizontal formula regions.

    This deliberately uses projection geometry instead of a separately licensed
    object detector. Superscripts, fraction bars and radicals are merged when
    their vertical spans are close enough.
    """
    rgb = light_background(image)
    gray = np.asarray(ImageOps.grayscale(rgb))
    active_rows = (gray < threshold).sum(axis=1) >= min_ink_pixels
    indices = np.flatnonzero(active_rows)
    if indices.size == 0:
        return [FormulaRegion(rgb, (0, 0, rgb.width, rgb.height))]

    spans: list[list[int]] = [[int(indices[0]), int(indices[0])]]
    for row in indices[1:]:
        row = int(row)
        if row - spans[-1][1] <= merge_gap + 1:
            spans[-1][1] = row
        else:
            spans.append([row, row])

    regions: list[FormulaRegion] = []
    for top_ink, bottom_ink in spans:
        band = gray[top_ink : bottom_ink + 1]
        active_cols = (band < threshold).sum(axis=0) > 0
        cols = np.flatnonzero(active_cols)
        if cols.size == 0:
            continue
        pad_x = max(8, int((bottom_ink - top_ink + 1) * 0.15))
        pad_y = max(6, int((bottom_ink - top_ink + 1) * 0.12))
        box = (
            max(0, int(cols.min()) - pad_x),
            max(0, top_ink - pad_y),
            min(rgb.width, int(cols.max()) + pad_x + 1),
            min(rgb.height, bottom_ink + pad_y + 1),
        )
        regions.append(FormulaRegion(rgb.crop(box), box))

    return regions or [FormulaRegion(rgb, (0, 0, rgb.width, rgb.height))]


def prepare_model_input(image: Image.Image, size: int = 384) -> np.ndarray:
    """Match the Pix2Text MFR model's documented image processor."""
    rgb = trim_background(image)
    resized = rgb.resize((size, size), Image.Resampling.BICUBIC)
    array = np.asarray(resized, dtype=np.float32) / 255.0
    array = (array - 0.5) / 0.5
    return np.transpose(array, (2, 0, 1))[None, ...]
