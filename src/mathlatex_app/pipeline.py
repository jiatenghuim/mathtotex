"""High-level screenshot-to-LaTeX pipeline."""

from __future__ import annotations

from PIL import Image

from .image_ops import split_formula_lines
from .recognizer import FormulaRecognizer


class MathLatexPipeline:
    def __init__(self, recognizer: FormulaRecognizer | None = None) -> None:
        self.recognizer = recognizer or FormulaRecognizer()

    def recognize_image(self, image: Image.Image, *, split_lines: bool = True) -> list[str]:
        regions = split_formula_lines(image) if split_lines else []
        images = [region.image for region in regions] if regions else [image]
        results = [self.recognizer.recognize(item) for item in images]
        return [result for result in results if result]

    @staticmethod
    def format_latex(lines: list[str]) -> str:
        if not lines:
            return ""
        if len(lines) == 1:
            return lines[0]
        body = " \\\\\n".join(lines)
        return "\\begin{aligned}\n" + body + "\n\\end{aligned}"

