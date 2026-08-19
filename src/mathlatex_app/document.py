"""Structured mixed OCR output and copy-format rendering."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

BlockKind = Literal["text", "formula"]
CopyStyle = Literal[
    "raw",
    "escaped",
    "dollar-inline",
    "dollar-display",
    "paren-inline",
    "bracket-display",
    "json",
]


@dataclass(frozen=True)
class OcrBlock:
    kind: BlockKind
    content: str
    box: tuple[int, int, int, int]
    confidence: float = 1.0


@dataclass(frozen=True)
class DocumentLine:
    blocks: tuple[OcrBlock, ...]


@dataclass(frozen=True)
class RecognitionDocument:
    lines: tuple[DocumentLine, ...]

    @property
    def formula_count(self) -> int:
        return sum(block.kind == "formula" for line in self.lines for block in line.blocks)

    @property
    def text_count(self) -> int:
        return sum(block.kind == "text" for line in self.lines for block in line.blocks)

    def render(self, style: CopyStyle = "raw") -> str:
        if style == "json":
            return json.dumps(self.render("raw"), ensure_ascii=False)
        if style == "escaped":
            return self.render("raw").replace("\\", "\\\\")

        rendered_lines = [self._render_line(line, style) for line in self.lines]
        rendered_lines = [line for line in rendered_lines if line]
        if not rendered_lines:
            return ""

        if style == "raw" and self.text_count == 0 and len(rendered_lines) > 1:
            return "\\begin{aligned}\n" + " \\\\\n".join(rendered_lines) + "\n\\end{aligned}"
        return "\n".join(rendered_lines)

    @staticmethod
    def _render_line(line: DocumentLine, style: CopyStyle) -> str:
        parts: list[str] = []
        for block in line.blocks:
            content = block.content.strip()
            if not content:
                continue
            if block.kind == "formula":
                content = _wrap_formula(content, style)
            parts.append(content)
        return " ".join(parts)


def _wrap_formula(formula: str, style: CopyStyle) -> str:
    wrappers = {
        "raw": ("", ""),
        "dollar-inline": ("$", "$"),
        "dollar-display": ("$$", "$$"),
        "paren-inline": ("\\(", "\\)"),
        "bracket-display": ("\\[", "\\]"),
    }
    prefix, suffix = wrappers.get(style, ("", ""))
    return f"{prefix}{formula}{suffix}"
