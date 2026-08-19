# Third-party notices

MathLaTeX's own source code is licensed under the MIT License. Its portable
distribution includes or depends on the following separately licensed works.

| Component | Use | License | Upstream |
| --- | --- | --- | --- |
| Pix2Text MFR ONNX model | Formula recognition weights and tokenizer | MIT | <https://huggingface.co/breezedeus/pix2text-mfr> |
| RapidOCR | Chinese/English text detection and recognition pipeline | Apache-2.0 | <https://github.com/RapidAI/RapidOCR> |
| PaddleOCR PP-OCR models | Text detection, orientation and recognition weights distributed by RapidOCR | Apache-2.0 | <https://github.com/PaddlePaddle/PaddleOCR> |
| ONNX Runtime | Local neural-network inference | MIT | <https://github.com/microsoft/onnxruntime> |
| NumPy | Array operations | BSD-3-Clause | <https://github.com/numpy/numpy> |
| Pillow | Image loading and screenshot access | HPND | <https://github.com/python-pillow/Pillow> |
| OpenCV | RapidOCR image processing | Apache-2.0 and bundled third-party terms | <https://github.com/opencv/opencv> |
| Shapely / GEOS | OCR polygon geometry | BSD-3-Clause / LGPL-2.1-or-later | <https://github.com/shapely/shapely> |
| Pyclipper | OCR polygon clipping | MIT | <https://github.com/fonttools/pyclipper> |
| OmegaConf, PyYAML | RapidOCR configuration | BSD-3-Clause / MIT | <https://github.com/omry/omegaconf> |
| Hugging Face Tokenizers | Token decoding | Apache-2.0 | <https://github.com/huggingface/tokenizers> |
| Python and Tkinter | Runtime and desktop UI | PSF-2.0 / Tcl-Tk terms | <https://www.python.org/> |
| PyInstaller | Portable Windows build tooling | GPL-2.0-or-later with bootloader exception | <https://pyinstaller.org/> |

The Pix2Text MFR model is downloaded separately by `scripts/download_models.ps1`
or included in binary release archives. RapidOCR carries the PP-OCR models used
for text OCR. No Ultralytics formula detector, AGPL component, or source code
from the earlier copied executable is included in this repository.

The user-supplied icon artwork is not covered by the MIT License. See
`assets/ICON_NOTICE.md`.

Copyright and license texts supplied by packaged Python dependencies remain in
their respective distributions. See each upstream project for its complete
license text and notices.
