"""Runtime paths shared by source and packaged builds."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def application_dir() -> Path:
    """Return the directory that owns the executable or source checkout."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def model_dir() -> Path:
    """Locate the separately distributed model directory."""
    override = os.environ.get("MATHLATEX_MODELS")
    if override:
        return Path(override).expanduser().resolve()
    return application_dir() / "models"


def mfr_dir() -> Path:
    return model_dir() / "mfr"

