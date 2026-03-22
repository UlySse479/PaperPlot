"""Render one preview image for every built-in PaperPlot template."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from typing import Any
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paperplot import managed_figure, plot_from_config


PREVIEW_CONFIGS: dict[str, dict[str, Any]] = {
    "ablation.study": {
        "paper": {"profile": "neurips", "style": "academic-bright"},
        "figure": {
            "template": "ablation.study",
            "data": {
                "component": ["Encoder", "Encoder", "Augment", "Augment"],
                "score": [82.1, 80.4, 81.7, 79.8],
                "variant": ["Base", "Removed", "Base", "Removed"],
            },
            "x": "component",
            "y": "score",
            "hue": "variant",
            "significance": [{"within": "each", "pairs": [["Base", "Removed"]], "text": "p<0.05"}],
            "title": "Grouped Ablation",
        },
    },
    "bar.ablation": {
        "paper": {"profile": "neurips", "style": "academic-bright"},
        "figure": {
            "template": "bar.ablation",
            "data": {"component": ["Full", "w/o aug", "w/o mixup", "w/o schedule"], "score": [82.4, 80.1, 79.6, 80.9]},
            "x": "component",
            "y": "score",
            "ylabel": "Accuracy (%)",
        },
    },
    "bar.default": {
        "paper": {"profile": "emnlp", "style": "nature-clean"},
        "figure": {
            "template": "bar.default",
            "data": {"system": ["Full", "Distilled", "Sparse", "Quantized"], "latency": [118, 94, 76, 63]},
            "x": "system",
            "y": "latency",
            "ylabel": "Latency (ms)",
            "title": "Resource Tradeoff",
        },
    },
    "box.default": {
        "paper": {"profile": "nature", "style": "nature-clean"},
        "figure": {
            "template": "box.default",
            "data": {
                "score": [0.81, 0.83, 0.82, 0.84, 0.85, 0.78, 0.79, 0.80, 0.81, 0.82],
                "method": ["Method A"] * 5 + ["Method B"] * 5,
            },
            "y": "score",
            "hue": "method",
            "ylabel": "F1 Score",
            "title": "Box Plot",
        },
    },
    "box.distribution_compare": {
        "paper": {"profile": "nature", "style": "nature-clean"},
        "figure": {
            "template": "box.distribution_compare",
            "data": {
                "score": [0.81, 0.83, 0.82, 0.84, 0.85, 0.78, 0.79, 0.80, 0.81, 0.82, 0.74, 0.76, 0.77, 0.78, 0.79],
                "method": ["Method A"] * 5 + ["Method B"] * 5 + ["Method C"] * 5,
            },
            "y": "score",
            "hue": "method",
            "ylabel": "F1 Score",
        },
    },
    "grouped_bar.benchmark_compare": {
        "paper": {"profile": "icml", "style": "academic-bright"},
        "figure": {
            "template": "grouped_bar.benchmark_compare",
            "data": {
                "benchmark": ["MMLU", "MMLU", "GSM8K", "GSM8K", "HumanEval", "HumanEval"],
                "score": [74.8, 77.2, 68.5, 71.9, 52.3, 58.7],
                "model": ["Baseline", "Improved", "Baseline", "Improved", "Baseline", "Improved"],
            },
            "x": "benchmark",
            "y": "score",
            "hue": "model",
            "ylabel": "Score",
        },
    },
    "grouped_bar.default": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "grouped_bar.default",
            "data": {
                "dataset": ["A", "A", "B", "B", "C", "C"],
                "value": [81.1, 83.4, 77.2, 79.1, 74.5, 76.0],
                "setting": ["Base", "Large", "Base", "Large", "Base", "Large"],
            },
            "x": "dataset",
            "y": "value",
            "hue": "setting",
            "ylabel": "Score",
            "title": "Grouped Bar",
        },
    },
    "heatmap.benchmark_matrix": {
        "paper": {"profile": "acl", "style": "academic-muted"},
        "figure": {
            "template": "heatmap.benchmark_matrix",
            "data": {
                "matrix": [[74.2, 69.5, 71.8, 73.0], [66.1, 72.8, 70.4, 71.2], [62.7, 68.3, 76.1, 69.4]],
                "x_labels": ["Arabic", "German", "Swahili", "Turkish"],
                "y_labels": ["Model A", "Aya-style", "Distilled"],
            },
        },
    },
    "heatmap.default": {
        "paper": {"profile": "acl", "style": "academic-muted"},
        "figure": {
            "template": "heatmap.default",
            "data": {
                "matrix": [[0.92, 0.75, 0.61], [0.71, 0.88, 0.67], [0.64, 0.69, 0.91]],
                "x_labels": ["Model A", "Model B", "Model C"],
                "y_labels": ["Dataset 1", "Dataset 2", "Dataset 3"],
            },
            "annotate": True,
            "title": "Heatmap",
        },
    },
    "hist.default": {
        "paper": {"profile": "acl", "style": "academic-muted"},
        "figure": {
            "template": "hist.default",
            "data": {"error": [-2.1, -1.8, -1.4, -1.1, -0.9, -0.7, -0.5, -0.2, 0.1, 0.2, 0.4, 0.6, 0.8, 1.1, 1.4, 1.8, 2.0]},
            "x": "error",
            "xlabel": "Prediction Error",
            "bins": 8,
        },
    },
    "line.default": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "line.default",
            "data": {
                "epoch": [1, 2, 3, 4, 1, 2, 3, 4],
                "acc": [68.2, 72.4, 74.8, 76.1, 66.9, 70.5, 73.0, 74.6],
                "method": ["Transformer"] * 4 + ["Hybrid"] * 4,
            },
            "x": "epoch",
            "y": "acc",
            "hue": "method",
            "ylabel": "Accuracy (%)",
            "title": "Line Plot",
        },
    },
    "line.scaling_law": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "line.scaling_law",
            "data": {
                "tokens": [10_000_000, 30_000_000, 100_000_000, 300_000_000, 1_000_000_000, 10_000_000, 30_000_000, 100_000_000, 300_000_000, 1_000_000_000],
                "loss": [2.52, 2.31, 2.14, 2.02, 1.94, 2.64, 2.41, 2.22, 2.10, 2.01],
                "run": ["Rectified Flow Transformer"] * 5 + ["Diffusion Baseline"] * 5,
            },
            "x": "tokens",
            "y": "loss",
            "hue": "run",
            "xscale": "log",
            "xformatter": "scientific",
            "xlabel": "Training Tokens",
            "ylabel": "Validation Loss",
        },
    },
    "line.sota_compare": {
        "paper": {"profile": "cvpr", "style": "grayscale-safe"},
        "figure": {
            "template": "line.sota_compare",
            "data": {
                "budget": [10, 20, 40, 80, 10, 20, 40, 80, 10, 20, 40, 80],
                "f1": [71.4, 74.6, 77.1, 78.5, 69.8, 73.0, 75.8, 77.3, 68.9, 71.5, 74.4, 76.1],
                "method": ["PaperPlot"] * 4 + ["Baseline+"] * 4 + ["Lightweight"] * 4,
            },
            "x": "budget",
            "y": "f1",
            "hue": "method",
            "xlabel": "Training Budget (GPU h)",
            "ylabel": "Macro-F1",
        },
    },
    "line.training_curve": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "line.training_curve",
            "data": {
                "epoch": [1, 2, 3, 4, 1, 2, 3, 4],
                "accuracy": [68.2, 72.4, 74.8, 76.1, 66.9, 70.5, 73.0, 74.6],
                "method": ["Transformer"] * 4 + ["Hybrid"] * 4,
            },
            "x": "epoch",
            "y": "accuracy",
            "hue": "method",
            "ylabel": "Accuracy (%)",
        },
    },
    "radar.default": {
        "paper": {"profile": "cvpr", "style": "grayscale-safe"},
        "figure": {
            "template": "radar.default",
            "data": {
                "categories": ["Accuracy", "Speed", "Robustness", "Memory", "Data Efficiency"],
                "series": [
                    {"label": "Baseline", "values": [0.72, 0.81, 0.68, 0.76, 0.70]},
                    {"label": "PaperPlot", "values": [0.84, 0.73, 0.79, 0.69, 0.82]},
                ],
            },
            "title": "Radar Summary",
        },
    },
    "scatter.default": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "scatter.default",
            "data": {
                "dim1": [1.0, 1.8, 2.4, 3.2, 1.3, 2.1, 2.9],
                "dim2": [2.2, 2.8, 2.5, 3.9, 1.4, 2.1, 3.1],
                "cluster": ["A", "A", "A", "A", "B", "B", "B"],
            },
            "x": "dim1",
            "y": "dim2",
            "hue": "cluster",
            "xlabel": "Embedding 1",
            "ylabel": "Embedding 2",
            "title": "Scatter Plot",
        },
    },
    "scatter.pareto_frontier": {
        "paper": {"profile": "cvpr", "style": "grayscale-safe"},
        "figure": {
            "template": "scatter.pareto_frontier",
            "data": {
                "latency": [28, 34, 42, 57, 71],
                "score": [78.8, 80.5, 81.0, 82.4, 82.8],
                "method": ["FastGS", "Mip-Splatting", "PixelSplat", "HumanFeedback", "PaperPlotVision"],
            },
            "x": "latency",
            "y": "score",
            "labels": "method",
            "xlabel": "Render Time (ms)",
            "ylabel": "Quality Score",
        },
    },
    "subplots.default": {
        "paper": {"profile": "icml", "style": "academic-muted"},
        "figure": {
            "template": "subplots.default",
            "data": {"placeholder": [1]},
            "ncols": 2,
            "figure_title": "Multi-Panel Summary",
            "panels": [
                {
                    "template": "line.training_curve",
                    "data": {"epoch": [1, 2, 3, 4], "acc": [68.2, 72.4, 74.8, 76.1]},
                    "x": "epoch",
                    "y": "acc",
                    "title": "Curve",
                },
                {
                    "template": "bar.default",
                    "data": {"model": ["A", "B", "C"], "score": [81.2, 82.7, 80.9]},
                    "x": "model",
                    "y": "score",
                    "title": "Bar",
                },
            ],
        },
    },
    "table.default": {
        "paper": {"profile": "emnlp", "style": "nature-clean"},
        "figure": {
            "template": "table.default",
            "data": [
                {"Model": "A", "F1": 81.2, "Params": 110},
                {"Model": "B", "F1": 82.7, "Params": 95},
                {"Model": "C", "F1": 80.9, "Params": 72},
            ],
            "title": "Summary Table",
        },
    },
    "table_mix.default": {
        "paper": {"profile": "emnlp", "style": "nature-clean"},
        "figure": {
            "template": "table_mix.default",
            "data": {"placeholder": [1]},
            "elements": [
                {
                    "template": "table.default",
                    "title": "Summary Table",
                    "row": 0,
                    "col": 0,
                    "data": [{"Model": "A", "F1": 81.2}, {"Model": "B", "F1": 82.7}],
                },
                {
                    "template": "bar.default",
                    "title": "F1 Score",
                    "row": 0,
                    "col": 1,
                    "data": {"model": ["A", "B"], "score": [81.2, 82.7]},
                    "x": "model",
                    "y": "score",
                },
            ],
        },
    },
    "table_mix.paper_summary": {
        "paper": {"profile": "cvpr", "style": "grayscale-safe"},
        "figure": {
            "template": "table_mix.paper_summary",
            "data": {"placeholder": [1]},
            "figure_title": "Vision Paper Summary",
            "figure_note": "Trade-off summary plus headline benchmark result.",
            "elements": [
                {
                    "template": "table.default",
                    "title": "Benchmark Summary",
                    "row": 0,
                    "col": 0,
                    "data": [
                        {"Model": "FastGS", "Score": 78.8, "FPS": 35.7},
                        {"Model": "Mip-Splatting", "Score": 80.5, "FPS": 29.4},
                        {"Model": "PaperPlotVision", "Score": 82.8, "FPS": 14.1},
                    ],
                },
                {
                    "template": "scatter.pareto_frontier",
                    "title": "Quality vs Speed",
                    "row": 0,
                    "col": 1,
                    "data": {
                        "latency": [28, 34, 42, 57, 71],
                        "score": [78.8, 80.5, 81.0, 82.4, 82.8],
                        "method": ["FastGS", "Mip-Splatting", "PixelSplat", "HumanFeedback", "PaperPlotVision"],
                    },
                    "x": "latency",
                    "y": "score",
                    "labels": "method",
                    "xlabel": "Render Time (ms)",
                    "ylabel": "Quality Score",
                },
            ],
        },
    },
}

CURATED_TEMPLATES = [
    "ablation.study",
    "bar.ablation",
    "box.distribution_compare",
    "grouped_bar.benchmark_compare",
    "heatmap.benchmark_matrix",
    "hist.default",
    "line.scaling_law",
    "line.sota_compare",
    "line.training_curve",
    "radar.default",
    "scatter.pareto_frontier",
    "subplots.default",
    "table_mix.paper_summary",
]


def render_template_previews(output_dir: str | Path, *, include_all: bool = False) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    template_names = sorted(PREVIEW_CONFIGS) if include_all else CURATED_TEMPLATES
    for template_name in template_names:
        config = PREVIEW_CONFIGS[template_name]
        payload = deepcopy(config)
        output_path = destination / f"{template_name.replace('.', '_')}.png"
        payload["figure"]["output"] = str(output_path)
        with managed_figure(plot_from_config(payload)):
            pass
        written.append(output_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PaperPlot template previews.")
    parser.add_argument("--output-dir", default="artifacts/template_previews", help="Directory to write preview images into.")
    parser.add_argument("--all", action="store_true", dest="include_all", help="Render all built-in templates instead of the curated subset.")
    args = parser.parse_args()

    written = render_template_previews(args.output_dir, include_all=args.include_all)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
