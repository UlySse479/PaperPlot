"""Small example gallery and regression fixtures for PaperPlot."""

from __future__ import annotations

from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import Any

from paperplot.core.mpl import prepare_matplotlib_env
from paperplot.core.renderer import plot_from_config


GALLERY_CASES: dict[str, dict[str, Any]] = {
    "line_sota_compare": {
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
            "title": "SOTA Comparison",
            "xlabel": "Training Budget (GPU h)",
            "ylabel": "Macro-F1",
            "output": "line_sota_compare.png",
            "size": "double",
        },
    },
    "line_training_curve": {
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
            "title": "Training Curve",
            "ylabel": "Accuracy (%)",
            "output": "line_training_curve.png",
        },
    },
    "bar_ablation": {
        "paper": {"profile": "neurips", "style": "academic-bright"},
        "figure": {
            "template": "bar.ablation",
            "data": {
                "component": ["Full", "w/o aug", "w/o mixup", "w/o schedule"],
                "score": [82.4, 80.1, 79.6, 80.9],
            },
            "x": "component",
            "y": "score",
            "title": "Ablation Study",
            "ylabel": "Accuracy (%)",
            "output": "bar_ablation.png",
        },
    },
    "scatter_clusters": {
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
            "title": "Cluster View",
            "xlabel": "Embedding 1",
            "ylabel": "Embedding 2",
            "output": "scatter_clusters.png",
        },
    },
    "hist_error_distribution": {
        "paper": {"profile": "acl", "style": "academic-muted"},
        "figure": {
            "template": "hist.default",
            "data": {
                "error": [
                    -2.1, -1.8, -1.4, -1.1, -0.9, -0.7, -0.5, -0.2,
                    0.1, 0.2, 0.4, 0.6, 0.8, 1.1, 1.4, 1.8, 2.0,
                ],
            },
            "x": "error",
            "title": "Error Distribution",
            "xlabel": "Prediction Error",
            "bins": 8,
            "output": "hist_error_distribution.png",
        },
    },
    "box_distribution_compare": {
        "paper": {"profile": "nature", "style": "nature-clean"},
        "figure": {
            "template": "box.distribution_compare",
            "data": {
                "score": [
                    0.81, 0.83, 0.82, 0.84, 0.85,
                    0.78, 0.79, 0.80, 0.81, 0.82,
                    0.74, 0.76, 0.77, 0.78, 0.79,
                ],
                "method": ["Method A"] * 5 + ["Method B"] * 5 + ["Method C"] * 5,
            },
            "y": "score",
            "hue": "method",
            "title": "Distribution Comparison",
            "ylabel": "F1 Score",
            "output": "box_distribution_compare.png",
        },
    },
    "heatmap_metrics": {
        "paper": {"profile": "acl", "style": "academic-muted"},
        "figure": {
            "template": "heatmap.default",
            "data": {
                "matrix": [[0.92, 0.75, 0.61], [0.71, 0.88, 0.67], [0.64, 0.69, 0.91]],
                "x_labels": ["Model A", "Model B", "Model C"],
                "y_labels": ["Dataset 1", "Dataset 2", "Dataset 3"],
            },
            "title": "Metric Heatmap",
            "annotate": True,
            "output": "heatmap_metrics.png",
        },
    },
    "bar_resource_tradeoff": {
        "paper": {"profile": "emnlp", "style": "nature-clean"},
        "figure": {
            "template": "bar.default",
            "data": {
                "system": ["Full", "Distilled", "Sparse", "Quantized"],
                "latency": [118, 94, 76, 63],
            },
            "x": "system",
            "y": "latency",
            "title": "Inference Cost",
            "ylabel": "Latency (ms)",
            "output": "bar_resource_tradeoff.png",
        },
    },
    "report_layout": {
        "paper": {"profile": "emnlp", "style": "nature-clean"},
        "figure": {
            "template": "table_mix.default",
            "data": {"placeholder": [1]},
            "output": "report_layout.png",
            "elements": [
                {
                    "template": "table.default",
                    "title": "Summary Table",
                    "panel_label": "(a)",
                    "row": 0,
                    "col": 0,
                    "data": [
                        {"Model": "A", "F1": 81.2, "Params": 110},
                        {"Model": "B", "F1": 82.7, "Params": 95},
                    ],
                },
                {
                    "template": "bar.default",
                    "title": "F1 Score",
                    "panel_label": "(b)",
                    "row": 0,
                    "col": 1,
                    "data": {"model": ["A", "B"], "score": [81.2, 82.7]},
                    "x": "model",
                    "y": "score",
                },
            ],
        },
    },
}


def get_gallery_case(name: str) -> dict[str, Any]:
    try:
        return deepcopy(GALLERY_CASES[name])
    except KeyError as exc:
        raise KeyError(f"Unknown gallery case: {name}") from exc


def render_gallery(output_dir: str | Path) -> list[Path]:
    prepare_matplotlib_env()
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for name, config in GALLERY_CASES.items():
        payload = deepcopy(config)
        payload["figure"]["output"] = str(destination / payload["figure"]["output"])
        with mpl.rc_context(rc=mpl.rcParamsDefault):
            fig, _, _ = plot_from_config(payload)
            fig.clf()
            plt.close(fig)
        written.append(destination / f"{name}.png")
    return written


def render_gallery_case_bytes(name: str) -> bytes:
    prepare_matplotlib_env()
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    payload = get_gallery_case(name)
    payload["figure"].pop("output", None)
    with mpl.rc_context(rc=mpl.rcParamsDefault):
        fig, _, spec = plot_from_config(payload)
        export = spec.get("export", {})
        buffer = BytesIO()
        fig.savefig(
            buffer,
            format="png",
            dpi=export.get("dpi", 300),
            bbox_inches=export.get("bbox_inches", "tight"),
            transparent=export.get("transparent", False),
        )
        fig.clf()
        plt.close(fig)
    return buffer.getvalue()
