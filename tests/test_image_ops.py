import numpy as np
from PIL import Image, ImageDraw

from mathlatex_app.image_ops import (
    light_background,
    prepare_model_input,
    split_formula_lines,
    trim_background,
)


def test_trim_background_removes_large_white_margin() -> None:
    image = Image.new("RGB", (200, 100), "white")
    ImageDraw.Draw(image).rectangle((70, 40, 130, 60), fill="black")
    cropped = trim_background(image)
    assert cropped.width < image.width
    assert cropped.height < image.height


def test_split_formula_lines_returns_visual_order() -> None:
    image = Image.new("RGB", (300, 180), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 180, 45), fill="black")
    draw.rectangle((40, 110, 250, 140), fill="black")
    regions = split_formula_lines(image)
    assert len(regions) == 2
    assert regions[0].box[1] < regions[1].box[1]


def test_prepare_model_input_shape_and_range() -> None:
    image = Image.new("RGB", (120, 40), "white")
    ImageDraw.Draw(image).line((10, 20, 110, 20), fill="black", width=3)
    value = prepare_model_input(image)
    assert value.shape == (1, 3, 384, 384)
    assert value.dtype == np.float32
    assert -1.0 <= float(value.min()) <= float(value.max()) <= 1.0


def test_dark_background_is_inverted() -> None:
    image = Image.new("RGB", (20, 20), "black")
    ImageDraw.Draw(image).rectangle((8, 8, 12, 12), fill="white")
    normalized = light_background(image)
    assert normalized.getpixel((0, 0)) == (255, 255, 255)
    assert normalized.getpixel((10, 10)) == (0, 0, 0)
