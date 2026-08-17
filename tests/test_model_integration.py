from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

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
