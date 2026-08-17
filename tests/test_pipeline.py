from mathlatex_app.pipeline import MathLatexPipeline


def test_format_single_formula() -> None:
    assert MathLatexPipeline.format_latex(["x^2"]) == "x^2"


def test_format_multiple_formulae() -> None:
    result = MathLatexPipeline.format_latex(["x=1", "y=2"])
    assert result == "\\begin{aligned}\nx=1 " + "\\\\\n" + "y=2\n\\end{aligned}"
