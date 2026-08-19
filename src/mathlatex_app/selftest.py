"""Repeatable end-to-end health check for source and portable builds."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .pipeline import MathLatexPipeline


def run_self_test() -> bool:
    math_font_path = Path("C:/Windows/Fonts/cambria.ttc")
    text_font_path = Path("C:/Windows/Fonts/arial.ttf")
    if not math_font_path.is_file() or not text_font_path.is_file():
        return False
    image = Image.new("RGB", (700, 210), "white")
    draw = ImageDraw.Draw(image)
    draw.text(
        (20, 20),
        "Course notes",
        font=ImageFont.truetype(str(text_font_path), 38),
        fill="black",
    )
    draw.text(
        (140, 105),
        "x² + y² = z²",
        font=ImageFont.truetype(str(math_font_path), 54),
        fill="black",
    )
    document = MathLatexPipeline().recognize_image(image)
    result = document.render().replace(" ", "")
    return (
        document.text_count >= 1
        and document.formula_count >= 1
        and "Coursenotes" in result
        and all(symbol in result for symbol in ("x", "y", "z"))
    )
