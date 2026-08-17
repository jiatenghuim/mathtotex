"""Repeatable end-to-end health check for source and portable builds."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .recognizer import FormulaRecognizer


def run_self_test() -> bool:
    font_path = Path("C:/Windows/Fonts/cambria.ttc")
    if not font_path.is_file():
        return False
    image = Image.new("RGB", (520, 110), "white")
    font = ImageFont.truetype(str(font_path), 54)
    ImageDraw.Draw(image).text((20, 20), "x² + y² = z²", font=font, fill="black")
    result = FormulaRecognizer().recognize(image, max_new_tokens=128).replace(" ", "")
    return all(symbol in result for symbol in ("x", "y", "z")) and result.count("2") >= 3

