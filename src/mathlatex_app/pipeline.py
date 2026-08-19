"""Reading-order mixed OCR pipeline for text and mathematical formulae."""

from __future__ import annotations

import re
from dataclasses import dataclass

from PIL import Image

from .document import DocumentLine, OcrBlock, RecognitionDocument
from .image_ops import light_background
from .recognizer import FormulaRecognizer
from .text_recognizer import TextRecognizer, TextRegion

_CJK_RE = re.compile(r"[\u3400-\u9fff]")
_GREEK_RE = re.compile(r"[\u0370-\u03ff]")
_LONG_WORD_RE = re.compile(r"[A-Za-z]{3,}")
_MATH_CHARACTERS = frozenset("=≠≈≤≥<>±×÷∑∏∫√∞∂∇→←↔∈∉⊂⊆∪∩∧∨^_+−")


@dataclass
class _LineGroup:
    regions: list[TextRegion]

    @property
    def top(self) -> int:
        return min(region.box[1] for region in self.regions)

    @property
    def bottom(self) -> int:
        return max(region.box[3] for region in self.regions)

    @property
    def center(self) -> float:
        return (self.top + self.bottom) / 2


class MathLatexPipeline:
    def __init__(
        self,
        formula_recognizer: FormulaRecognizer | None = None,
        text_recognizer: TextRecognizer | None = None,
    ) -> None:
        self.formula_recognizer = formula_recognizer or FormulaRecognizer()
        self.text_recognizer = text_recognizer or TextRecognizer()

    def recognize_image(self, image: Image.Image) -> RecognitionDocument:
        normalized = light_background(image)
        regions = self.text_recognizer.recognize(normalized)
        line_groups = group_regions_into_lines(regions)
        lines: list[DocumentLine] = []

        for group in line_groups:
            runs = split_line_runs(group.regions, normalized.width)
            blocks: list[OcrBlock] = []
            for run in runs:
                text = " ".join(region.text for region in run).strip()
                total_width = sum(max(1, region.width) for region in run)
                score = sum(region.score * max(1, region.width) for region in run) / total_width
                box = union_box([region.box for region in run])
                if looks_like_formula(text, score):
                    crop_box = expand_box(box, normalized.size, padding=8)
                    crop = normalized.crop(crop_box)
                    formula = self.formula_recognizer.recognize(crop)
                    content = formula or text
                    kind = "formula"
                else:
                    content = text
                    kind = "text"
                blocks.append(OcrBlock(kind, content, box, score))
            if blocks:
                lines.append(DocumentLine(tuple(blocks)))

        return RecognitionDocument(tuple(lines))

    @staticmethod
    def format_latex(lines: list[str]) -> str:
        """Backward-compatible helper retained for API users."""
        if not lines:
            return ""
        if len(lines) == 1:
            return lines[0]
        return "\\begin{aligned}\n" + " \\\\\n".join(lines) + "\n\\end{aligned}"


def looks_like_formula(text: str, score: float = 1.0) -> bool:
    compact = text.strip()
    if not compact:
        return False
    cjk_count = len(_CJK_RE.findall(compact))
    long_words = _LONG_WORD_RE.findall(compact)
    has_greek = bool(_GREEK_RE.search(compact))
    math_count = sum(character in _MATH_CHARACTERS for character in compact)

    if cjk_count >= 2:
        return False
    if len(long_words) >= 3:
        return False
    if has_greek or math_count >= 1:
        return True
    if score < 0.72 and not cjk_count and len(compact) <= 120:
        return True

    alpha_groups = re.findall(r"[A-Za-z]+", compact)
    has_structure = any(character in compact for character in "()[]{}²³₀₁₂₃₄₅₆₇₈₉")
    return (
        len(compact) <= 60
        and len(alpha_groups) <= 2
        and has_structure
        and any(character.isalpha() for character in compact)
    )


def group_regions_into_lines(regions: list[TextRegion]) -> list[_LineGroup]:
    groups: list[_LineGroup] = []
    ordered = sorted(regions, key=lambda item: ((item.box[1] + item.box[3]) / 2, item.box[0]))
    for region in ordered:
        best: _LineGroup | None = None
        best_distance = float("inf")
        for group in groups:
            overlap = max(0, min(region.box[3], group.bottom) - max(region.box[1], group.top))
            min_height = max(1, min(region.height, group.bottom - group.top))
            center_distance = abs((region.box[1] + region.box[3]) / 2 - group.center)
            max_height = max(region.height, group.bottom - group.top)
            is_same_line = overlap / min_height >= 0.4 or center_distance <= 0.35 * max_height
            if is_same_line and center_distance < best_distance:
                best = group
                best_distance = center_distance
        if best is None:
            groups.append(_LineGroup([region]))
        else:
            best.regions.append(region)

    groups.sort(key=lambda group: (group.top, min(region.box[0] for region in group.regions)))
    for group in groups:
        group.regions.sort(key=lambda region: region.box[0])
    return groups


def split_line_runs(regions: list[TextRegion], image_width: int) -> list[list[TextRegion]]:
    if not regions:
        return []
    heights = sorted(region.height for region in regions)
    median_height = heights[len(heights) // 2]
    gap_limit = max(4 * median_height, int(image_width * 0.08))
    runs: list[list[TextRegion]] = [[regions[0]]]
    for region in regions[1:]:
        gap = region.box[0] - runs[-1][-1].box[2]
        if gap > gap_limit:
            runs.append([region])
        else:
            runs[-1].append(region)
    return runs


def union_box(boxes: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def expand_box(
    box: tuple[int, int, int, int],
    image_size: tuple[int, int],
    *,
    padding: int,
) -> tuple[int, int, int, int]:
    width, height = image_size
    return (
        max(0, box[0] - padding),
        max(0, box[1] - padding),
        min(width, box[2] + padding),
        min(height, box[3] + padding),
    )
