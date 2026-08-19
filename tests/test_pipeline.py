from PIL import Image

from mathlatex_app.pipeline import MathLatexPipeline, looks_like_formula
from mathlatex_app.text_recognizer import TextRegion


def test_format_single_formula() -> None:
    assert MathLatexPipeline.format_latex(["x^2"]) == "x^2"


def test_format_multiple_formulae() -> None:
    result = MathLatexPipeline.format_latex(["x=1", "y=2"])
    assert result == "\\begin{aligned}\nx=1 " + "\\\\\n" + "y=2\n\\end{aligned}"


def test_formula_classifier_distinguishes_notes_and_equations() -> None:
    assert looks_like_formula("µθ = argmax Qθ(st, µθ(st)).", 0.97)
    assert looks_like_formula("x² + y² = z²", 0.99)
    assert not looks_like_formula("强化学习课堂笔记：策略网络负责选择动作。", 0.99)
    assert not looks_like_formula("The loss is evaluated using the actor network.", 0.99)
    assert not looks_like_formula("(4)", 0.99)


class FakeFormulaRecognizer:
    def recognize(self, _image: Image.Image) -> str:
        return r"x^2+y^2=z^2"


class FakeTextRecognizer:
    def recognize(self, _image: Image.Image) -> list[TextRegion]:
        return [
            TextRegion("课堂笔记", 0.99, (10, 10, 100, 35)),
            TextRegion("x² + y² = z²", 0.98, (30, 60, 220, 95)),
            TextRegion("English notes", 0.99, (10, 120, 180, 145)),
        ]


def test_mixed_pipeline_preserves_reading_order() -> None:
    pipeline = MathLatexPipeline(FakeFormulaRecognizer(), FakeTextRecognizer())
    document = pipeline.recognize_image(Image.new("RGB", (300, 180), "white"))
    assert document.text_count == 2
    assert document.formula_count == 1
    assert document.render("dollar-inline") == "课堂笔记\n$x^2+y^2=z^2$\nEnglish notes"
