import os
import sys
from pathlib import Path

import matplotlib
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-paperplot")
matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def _close_matplotlib_figures():
    yield
    import matplotlib.pyplot as plt

    plt.close("all")
