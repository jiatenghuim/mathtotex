from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from mathlatex_app.pipeline import MathLatexPipeline
from mathlatex_app.recognizer import FormulaRecognizer

MODEL_DIR = Path(__file__).parents[1] / "models" / "mfr"


@pytest.mark.skipif(not (MODEL_DIR / "encoder_model.onnx").is_file(), reason="model not installed")
def test_real_model_recognizes_a_simple_formula() -> None:
    image = Image.new("RGB", (520, 110), "white")
    font_path = Path("C:/Windows/Fonts/cambria.ttc")
    if not font_path.is_file():
        pytest.skip("Cambria is not installed")
    font = ImageFont.truetype(str(font_path), 54)
    ImageDraw.Draw(image).text((20, 20), "x² + y² = z²", font=font, fill="black")
    result = FormulaRecognizer(MODEL_DIR).recognize(image, max_new_tokens=128)
    normalized = result.replace(" ", "")
    assert "x" in normalized
    assert "y" in normalized
    assert "z" in normalized
    assert normalized.count("2") >= 3


@pytest.mark.skipif(not (MODEL_DIR / "encoder_model.onnx").is_file(), reason="model not installed")
def test_real_mixed_ocr_recognizes_chinese_formula_and_english() -> None:
    chinese_font_path = Path("C:/Windows/Fonts/msyh.ttc")
    math_font_path = Path("C:/Windows/Fonts/cambria.ttc")
    if not chinese_font_path.is_file() or not math_font_path.is_file():
        pytest.skip("required Windows fonts are not installed")

    image = Image.new("RGB", (1200, 330), "white")
    draw = ImageDraw.Draw(image)
    text_font = ImageFont.truetype(str(chinese_font_path), 42)
    math_font = ImageFont.truetype(str(math_font_path), 54)
    draw.text((30, 25), "强化学习课堂笔记", font=text_font, fill="black")
    draw.text((300, 125), "x² + y² = z²", font=math_font, fill="black")
    draw.text((30, 235), "Future rewards", font=text_font, fill="black")

    document = MathLatexPipeline(FormulaRecognizer(MODEL_DIR)).recognize_image(image)
    rendered = document.render("dollar-inline").replace(" ", "")
    assert document.text_count == 2
    assert document.formula_count == 1
    assert "强化学习课堂笔记" in rendered
    assert "Futurewards" not in rendered
    assert "Futurerewards" in rendered
    assert all(symbol in rendered for symbol in ("x", "y", "z"))
