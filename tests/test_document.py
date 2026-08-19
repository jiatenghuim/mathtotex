from mathlatex_app.document import DocumentLine, OcrBlock, RecognitionDocument


def sample_document() -> RecognitionDocument:
    return RecognitionDocument(
        (
            DocumentLine((OcrBlock("text", "课堂笔记", (0, 0, 80, 20)),)),
            DocumentLine((OcrBlock("formula", r"x^2+y^2=z^2", (0, 30, 120, 55)),)),
        )
    )


def test_copy_styles_only_wrap_formula_blocks() -> None:
    document = sample_document()
    assert document.render("dollar-inline") == "课堂笔记\n$x^2+y^2=z^2$"
    assert document.render("dollar-display") == "课堂笔记\n$$x^2+y^2=z^2$$"
    assert document.render("paren-inline") == "课堂笔记\n\\(x^2+y^2=z^2\\)"
    assert document.render("bracket-display") == "课堂笔记\n\\[x^2+y^2=z^2\\]"


def test_escaped_and_json_styles_preserve_chinese() -> None:
    document = sample_document()
    assert document.render("escaped") == "课堂笔记\nx^2+y^2=z^2"
    assert document.render("json") == '"课堂笔记\\nx^2+y^2=z^2"'


def test_formula_only_raw_output_keeps_aligned_behavior() -> None:
    document = RecognitionDocument(
        (
            DocumentLine((OcrBlock("formula", "x=1", (0, 0, 10, 10)),)),
            DocumentLine((OcrBlock("formula", "y=2", (0, 20, 10, 30)),)),
        )
    )
    assert document.render() == "\\begin{aligned}\nx=1 \\\\\ny=2\n\\end{aligned}"

