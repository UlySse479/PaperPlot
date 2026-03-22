"""Generate baseline PNGs for PaperPlot visual regression tests."""

from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-paperplot")

from paperplot.gallery import GALLERY_CASES, render_gallery_case_bytes


def main() -> None:
    baseline_dir = Path("tests/baselines")
    baseline_dir.mkdir(parents=True, exist_ok=True)

    for name in GALLERY_CASES:
        (baseline_dir / f"{name}.png").write_bytes(render_gallery_case_bytes(name))


if __name__ == "__main__":
    main()
