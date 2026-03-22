"""Matplotlib environment helpers."""

from __future__ import annotations

import os
from pathlib import Path


def prepare_matplotlib_env() -> None:
    """Point Matplotlib at a writable cache dir when none is configured."""
    if os.environ.get("MPLCONFIGDIR"):
        return

    default = Path.home() / ".config" / "matplotlib"
    if default.exists() and os.access(default, os.W_OK):
        return

    fallback = Path("/tmp/matplotlib-paperplot")
    fallback.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(fallback)
