"""Print ONNX input/output metadata for local development."""

from __future__ import annotations

import argparse
from pathlib import Path

import onnxruntime as ort


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="+", type=Path)
    args = parser.parse_args()

    for model_path in args.models:
        session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        print(f"\n[{model_path}]")
        print("inputs:")
        for value in session.get_inputs():
            print(f"  {value.name}: {value.type} {value.shape}")
        print("outputs:")
        for value in session.get_outputs():
            print(f"  {value.name}: {value.type} {value.shape}")


if __name__ == "__main__":
    main()
