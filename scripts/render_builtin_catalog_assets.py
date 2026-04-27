"""Render catalog assets for built-in PaperPlot profiles, styles, and templates."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paperplot import managed_figure, plot_from_config
from render_template_previews import render_template_previews


PROFILE_PREVIEWS: dict[str, dict[str, Any]] = {
    "acl": {
        "paper": {"profile": "acl", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "size": "single",
            "data": {
                "epoch": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                "accuracy": [68.2, 72.1, 74.0, 75.4, 76.0, 66.8, 70.4, 72.7, 73.9, 74.6, 64.9, 69.1, 71.4, 72.8, 73.5],
                "method": ["PaperPlot"] * 5 + ["Strong Baseline"] * 5 + ["Compact Model"] * 5,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Accuracy (%)",
            "title": "ACL Single-Column Preview",
        },
    },
    "cvpr": {
        "paper": {"profile": "cvpr", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "size": "single",
            "data": {
                "epoch": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                "accuracy": [68.2, 72.1, 74.0, 75.4, 76.0, 66.8, 70.4, 72.7, 73.9, 74.6, 64.9, 69.1, 71.4, 72.8, 73.5],
                "method": ["PaperPlot"] * 5 + ["Strong Baseline"] * 5 + ["Compact Model"] * 5,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Accuracy (%)",
            "title": "CVPR Single-Column Preview",
        },
    },
    "emnlp": {
        "paper": {"profile": "emnlp", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "size": "single",
            "data": {
                "epoch": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                "accuracy": [68.2, 72.1, 74.0, 75.4, 76.0, 66.8, 70.4, 72.7, 73.9, 74.6, 64.9, 69.1, 71.4, 72.8, 73.5],
                "method": ["PaperPlot"] * 5 + ["Strong Baseline"] * 5 + ["Compact Model"] * 5,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Accuracy (%)",
            "title": "EMNLP Single-Column Preview",
        },
    },
    "icml": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "size": "single",
            "data": {
                "epoch": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                "accuracy": [68.2, 72.1, 74.0, 75.4, 76.0, 66.8, 70.4, 72.7, 73.9, 74.6, 64.9, 69.1, 71.4, 72.8, 73.5],
                "method": ["PaperPlot"] * 5 + ["Strong Baseline"] * 5 + ["Compact Model"] * 5,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Accuracy (%)",
            "title": "ICML Single-Column Preview",
        },
    },
    "nature": {
        "paper": {"profile": "nature", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "size": "single",
            "data": {
                "epoch": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                "accuracy": [68.2, 72.1, 74.0, 75.4, 76.0, 66.8, 70.4, 72.7, 73.9, 74.6, 64.9, 69.1, 71.4, 72.8, 73.5],
                "method": ["PaperPlot"] * 5 + ["Strong Baseline"] * 5 + ["Compact Model"] * 5,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Accuracy (%)",
            "title": "Nature Single-Column Preview",
        },
    },
    "neurips": {
        "paper": {"profile": "neurips", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "size": "single",
            "data": {
                "epoch": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                "accuracy": [68.2, 72.1, 74.0, 75.4, 76.0, 66.8, 70.4, 72.7, 73.9, 74.6, 64.9, 69.1, 71.4, 72.8, 73.5],
                "method": ["PaperPlot"] * 5 + ["Strong Baseline"] * 5 + ["Compact Model"] * 5,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Accuracy (%)",
            "title": "NeurIPS Single-Column Preview",
        },
    },
}

STYLE_PREVIEWS: dict[str, dict[str, Any]] = {
    "default": {
        "paper": {"profile": "icml", "style": "default"},
        "figure": {
            "template": "line.default",
            "data": {
                "epoch": [1, 2, 3, 4, 5] * 4,
                "score": [66.4, 69.9, 72.2, 74.0, 75.1, 67.9, 70.8, 73.5, 75.4, 76.0, 64.8, 68.6, 70.9, 72.5, 73.6, 62.9, 66.1, 68.7, 70.1, 71.5],
                "method": ["Default"] * 5 + ["Academic"] * 5 + ["Compact"] * 5 + ["Robust"] * 5,
            },
            "x": "epoch",
            "y": "score",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Score",
            "title": "Default Style Preview",
        },
    },
    "academic-muted": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "line.default",
            "data": {
                "epoch": [1, 2, 3, 4, 5] * 4,
                "score": [66.4, 69.9, 72.2, 74.0, 75.1, 67.9, 70.8, 73.5, 75.4, 76.0, 64.8, 68.6, 70.9, 72.5, 73.6, 62.9, 66.1, 68.7, 70.1, 71.5],
                "method": ["Default"] * 5 + ["Academic"] * 5 + ["Compact"] * 5 + ["Robust"] * 5,
            },
            "x": "epoch",
            "y": "score",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Score",
            "title": "Academic Muted Preview",
        },
    },
    "academic-bright": {
        "paper": {"profile": "icml", "style": "academic-bright"},
        "figure": {
            "template": "line.default",
            "data": {
                "epoch": [1, 2, 3, 4, 5] * 4,
                "score": [66.4, 69.9, 72.2, 74.0, 75.1, 67.9, 70.8, 73.5, 75.4, 76.0, 64.8, 68.6, 70.9, 72.5, 73.6, 62.9, 66.1, 68.7, 70.1, 71.5],
                "method": ["Default"] * 5 + ["Academic"] * 5 + ["Compact"] * 5 + ["Robust"] * 5,
            },
            "x": "epoch",
            "y": "score",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Score",
            "title": "Academic Bright Preview",
        },
    },
    "grayscale-safe": {
        "paper": {"profile": "icml", "style": "grayscale-safe"},
        "figure": {
            "template": "line.default",
            "data": {
                "epoch": [1, 2, 3, 4, 5] * 4,
                "score": [66.4, 69.9, 72.2, 74.0, 75.1, 67.9, 70.8, 73.5, 75.4, 76.0, 64.8, 68.6, 70.9, 72.5, 73.6, 62.9, 66.1, 68.7, 70.1, 71.5],
                "method": ["Default"] * 5 + ["Academic"] * 5 + ["Compact"] * 5 + ["Robust"] * 5,
            },
            "x": "epoch",
            "y": "score",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Score",
            "title": "Grayscale Safe Preview",
        },
    },
    "nature-clean": {
        "paper": {"profile": "icml", "style": "nature-clean"},
        "figure": {
            "template": "line.default",
            "data": {
                "epoch": [1, 2, 3, 4, 5] * 4,
                "score": [66.4, 69.9, 72.2, 74.0, 75.1, 67.9, 70.8, 73.5, 75.4, 76.0, 64.8, 68.6, 70.9, 72.5, 73.6, 62.9, 66.1, 68.7, 70.1, 71.5],
                "method": ["Default"] * 5 + ["Academic"] * 5 + ["Compact"] * 5 + ["Robust"] * 5,
            },
            "x": "epoch",
            "y": "score",
            "hue": "method",
            "xlabel": "Epoch",
            "ylabel": "Score",
            "title": "Nature Clean Preview",
        },
    },
}


def _render_configs(configs: dict[str, dict[str, Any]], output_dir: Path, prefix: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, config in sorted(configs.items()):
        payload = deepcopy(config)
        output_path = output_dir / f"{prefix}_{name.replace('.', '_').replace('-', '_')}.png"
        payload["figure"]["output"] = str(output_path)
        with managed_figure(plot_from_config(payload)):
            pass
        written.append(output_path)
    return written


def render_builtin_catalog_assets(output_dir: str | Path) -> list[Path]:
    root = Path(output_dir)
    written: list[Path] = []
    written.extend(render_template_previews(root / "templates", include_all=True))
    written.extend(_render_configs(PROFILE_PREVIEWS, root / "profiles", "profile"))
    written.extend(_render_configs(STYLE_PREVIEWS, root / "styles", "style"))
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Render built-in PaperPlot catalog assets.")
    parser.add_argument(
        "--output-dir",
        default="docs/builtins",
        help="Directory to write profile/style/template previews into.",
    )
    args = parser.parse_args()

    written = render_builtin_catalog_assets(args.output_dir)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
