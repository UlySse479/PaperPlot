from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg

from paperplot.gallery import GALLERY_CASES, render_gallery_case_bytes


BASELINE_DIR = Path(__file__).resolve().parent / "baselines"

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pixel_hash(data: bytes) -> str:
    image = mpimg.imread(BytesIO(data), format="png")
    return _sha256(image.tobytes())


def test_visual_baselines_exist():
    missing = [name for name in GALLERY_CASES if not (BASELINE_DIR / f"{name}.png").exists()]
    assert not missing, f"Missing visual baselines: {missing}"


def test_visual_regression_contract():
    mismatches = []
    for name in GALLERY_CASES:
        actual = render_gallery_case_bytes(name)
        expected_path = BASELINE_DIR / f"{name}.png"
        expected = expected_path.read_bytes()
        if _pixel_hash(actual) != _pixel_hash(expected):
            mismatches.append(name)

    assert not mismatches, f"Visual regression mismatches: {mismatches}"
