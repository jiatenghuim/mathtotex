"""ONNX-based formula recognition with no framework runtime dependency."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image
from tokenizers import Tokenizer

from .image_ops import prepare_model_input
from .paths import mfr_dir


class ModelFilesMissingError(FileNotFoundError):
    pass


class FormulaRecognizer:
    """Greedy decoder for the MIT-licensed Pix2Text MFR ONNX model."""

    required_files = ("encoder_model.onnx", "decoder_model.onnx", "tokenizer.json")

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = Path(directory or mfr_dir())
        missing = [name for name in self.required_files if not (self.directory / name).is_file()]
        if missing:
            joined = ", ".join(missing)
            raise ModelFilesMissingError(f"模型文件不完整：{joined}\n模型目录：{self.directory}")

        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        providers = ["CPUExecutionProvider"]
        self.encoder = ort.InferenceSession(
            str(self.directory / "encoder_model.onnx"),
            sess_options=options,
            providers=providers,
        )
        self.decoder = ort.InferenceSession(
            str(self.directory / "decoder_model.onnx"),
            sess_options=options,
            providers=providers,
        )
        self.tokenizer = Tokenizer.from_file(str(self.directory / "tokenizer.json"))

    def recognize(self, image: Image.Image, *, max_new_tokens: int = 512) -> str:
        pixels = prepare_model_input(image)
        hidden = self.encoder.run(None, {"pixel_values": pixels})[0]
        token_ids = [2]
        for _ in range(max_new_tokens):
            decoder_input = np.asarray([token_ids], dtype=np.int64)
            logits = self.decoder.run(
                None,
                {
                    "input_ids": decoder_input,
                    "encoder_hidden_states": hidden,
                },
            )[0]
            next_id = int(np.argmax(logits[0, -1]))
            if next_id == 2:
                break
            token_ids.append(next_id)

        # Exclude the decoder start token. The tokenizer removes any remaining
        # model-control symbols and joins SentencePiece fragments.
        return self.tokenizer.decode(token_ids[1:], skip_special_tokens=True).strip()

