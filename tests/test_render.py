import json
from pathlib import Path
import subprocess
import sys

import matplotlib
from matplotlib.legend import Legend

matplotlib.use("Agg")

from paperplot import managed_figure, plot, plot_from_config, use_style
from paperplot.gallery import GALLERY_CASES, render_gallery


def test_use_style_applies_size_token():
    spec = use_style(profile="icml", visual="academic-muted", size="double")
    assert tuple(spec["figure"]["figsize"]) == (6.8, 3.0)


def test_plot_line_smoke(tmp_path: Path):
    data = {
        "epoch": [1, 2, 3, 1, 2, 3],
        "acc": [70, 73, 75, 68, 71, 74],
        "method": ["A", "A", "A", "B", "B", "B"],
    }
    output = tmp_path / "acc.pdf"

    fig, ax, spec = plot(
        template="line.sota_compare",
        data=data,
        x="epoch",
        y="acc",
        hue="method",
        output=str(output),
    )

    assert ax.get_xlabel() == "Epoch"
    assert spec["template"]["chart_type"] == "line"
    assert output.exists()
    fig.clf()


def test_plot_line_supports_primary_and_extra_legends():
    data = {
        "epoch": [1, 2, 3, 1, 2, 3],
        "acc": [70, 73, 75, 68, 71, 74],
        "method": ["A", "A", "A", "B", "B", "B"],
    }

    fig, ax, _ = plot(
        template="line.sota_compare",
        data=data,
        x="epoch",
        y="acc",
        hue="method",
        legend="upper left",
        legend_bbox_to_anchor=[0.0, 1.02],
        legend_ncol=2,
        extra_legends=[
            {
                "title": "Metric",
                "loc": "lower right",
                "entries": [
                    {"label": "Main", "color": "#666666", "linestyle": "--"},
                    {"label": "Ref", "color": "#999999", "linestyle": "-"},
                ],
            }
        ],
    )

    legends = [artist for artist in ax.get_children() if isinstance(artist, Legend)]
    assert len(legends) == 2
    assert ax.get_legend().get_title().get_text() == "Metric"
    fig.clf()


def test_plot_from_config_dict_smoke(tmp_path: Path):
    output = tmp_path / "ablation.pdf"
    config = {
        "paper": {
            "profile": "neurips",
            "style": "academic-bright",
        },
        "figure": {
            "template": "bar.ablation",
            "data": {
                "component": ["base", "w/o aug", "w/o schedule"],
                "score": [82.1, 79.8, 80.4],
            },
            "x": "component",
            "y": "score",
            "output": str(output),
            "title": "Ablation on Training Components",
        },
    }

    fig, ax, spec = plot_from_config(config)

    assert spec["template"]["name"] == "bar.ablation"
    assert spec["name"] == "academic-bright"
    assert ax.get_title() == "Ablation on Training Components"
    assert output.exists()
    fig.clf()


def test_color_advisor_persists_series_colors_across_figures(tmp_path: Path):
    persist_path = tmp_path / "paper-colors.json"
    config_a = {
        "paper": {
            "profile": "icml",
            "style": "academic-muted",
            "color_advisor": {
                "enabled": True,
                "persist_path": str(persist_path),
                "namespace": "demo-paper",
                "preferred_order": ["Ours", "Baseline"],
            },
        },
        "figure": {
            "template": "line.sota_compare",
            "data": {
                "epoch": [1, 2, 1, 2],
                "acc": [80, 82, 77, 79],
                "method": ["Baseline", "Baseline", "Ours", "Ours"],
            },
            "x": "epoch",
            "y": "acc",
            "hue": "method",
        },
    }
    config_b = {
        "paper": {
            "profile": "icml",
            "style": "academic-muted",
            "color_advisor": {
                "enabled": True,
                "persist_path": str(persist_path),
                "namespace": "demo-paper",
            },
        },
        "figure": {
            "template": "line.sota_compare",
            "data": {
                "epoch": [1, 2, 1, 2],
                "acc": [77, 79, 80, 82],
                "method": ["Ours", "Ours", "Baseline", "Baseline"],
            },
            "x": "epoch",
            "y": "acc",
            "hue": "method",
        },
    }

    fig_a, ax_a, _ = plot_from_config(config_a)
    fig_b, ax_b, _ = plot_from_config(config_b)

    colors_a = {line.get_label(): line.get_color() for line in ax_a.get_lines()}
    colors_b = {line.get_label(): line.get_color() for line in ax_b.get_lines()}

    assert colors_a["Ours"] == colors_b["Ours"]
    assert colors_a["Baseline"] == colors_b["Baseline"]
    assert persist_path.exists()
    fig_a.clf()
    fig_b.clf()


def test_color_advisor_prefers_separated_two_series_palette():
    config = {
        "paper": {
            "profile": "icml",
            "style": "academic-muted",
            "color_advisor": {
                "enabled": True,
                "usage": "manuscript",
                "tone": "restrained",
            },
        },
        "figure": {
            "template": "line.sota_compare",
            "data": {
                "epoch": [1, 2, 1, 2],
                "acc": [80, 82, 77, 79],
                "method": ["Baseline", "Baseline", "Ours", "Ours"],
            },
            "x": "epoch",
            "y": "acc",
            "hue": "method",
        },
    }

    fig, ax, spec = plot_from_config(config)

    advisor_id = spec["palette"]["advisor"]["template"]["id"]
    ours = next(line for line in ax.get_lines() if line.get_label() == "Ours").get_color()
    baseline = next(line for line in ax.get_lines() if line.get_label() == "Baseline").get_color()

    assert advisor_id == "editorial-lines-light"
    assert ours != baseline
    fig.clf()


def test_color_advisor_drops_stale_persisted_colors(tmp_path: Path):
    persist_path = tmp_path / "paper-colors.json"
    persist_path.write_text(
        json.dumps(
            {
                "version": 1,
                "papers": {
                    "paper-demo": {
                        "series": {
                            "Ours": "#2F5A78",
                            "Baseline": "#55738A",
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    config = {
        "paper": {
            "profile": "icml",
            "style": "academic-muted",
            "color_advisor": {
                "enabled": True,
                "usage": "manuscript",
                "tone": "restrained",
                "namespace": "paper-demo",
                "persist_path": str(persist_path),
            },
        },
        "figure": {
            "template": "line.sota_compare",
            "data": {
                "epoch": [1, 2, 1, 2],
                "acc": [80, 82, 77, 79],
                "method": ["Baseline", "Baseline", "Ours", "Ours"],
            },
            "x": "epoch",
            "y": "acc",
            "hue": "method",
        },
    }

    fig, ax, spec = plot_from_config(config)

    palette = set(spec["palette"]["colors"])
    colors = {line.get_label(): line.get_color() for line in ax.get_lines()}

    assert spec["palette"]["advisor"]["template"]["id"] == "editorial-lines-light"
    assert colors["Ours"] in palette
    assert colors["Baseline"] in palette
    fig.clf()


def test_color_advisor_heatmap_uses_recommended_cmap():
    config = {
        "paper": {
            "profile": "icml",
            "style": "academic-muted",
            "color_advisor": {
                "enabled": True,
                "usage": "manuscript",
            },
        },
        "figure": {
            "template": "heatmap.default",
            "data": {
                "matrix": [[0.1, 0.4], [0.7, 0.9]],
                "x_labels": ["A", "B"],
                "y_labels": ["X", "Y"],
            },
        },
    }

    fig, ax, spec = plot_from_config(config)

    image = ax.images[0]
    assert spec["palette"]["advisor"]["template"]["chart_type"] == "heatmap"
    assert image.get_cmap().name == spec["palette"]["advisor"]["template"]["id"]
    fig.clf()


def test_plot_box_supports_hue_legend_controls():
    data = {
        "score": [0.81, 0.83, 0.82, 0.84, 0.78, 0.79, 0.80, 0.81],
        "method": ["A"] * 4 + ["B"] * 4,
    }

    fig, ax, _ = plot(
        template="box.default",
        data=data,
        y="score",
        hue="method",
        legend="upper center",
        legend_title="Method",
        legend_bbox_to_anchor=[0.5, 1.05],
        legend_ncol=2,
    )

    legend = ax.get_legend()
    assert legend is not None
    assert legend.get_title().get_text() == "Method"
    assert len(legend.texts) == 2
    fig.clf()


def test_plot_from_config_requires_template_and_data():
    bad_config = {"paper": {"profile": "icml"}, "figure": {}}

    try:
        plot_from_config(bad_config)
    except ValueError as exc:
        assert "template" in str(exc)
    else:
        raise AssertionError("Expected config validation failure.")


def test_render_gallery_writes_all_cases(tmp_path: Path):
    written = render_gallery(tmp_path)

    assert len(written) == len(GALLERY_CASES)
    for path in written:
        assert path.exists()


def test_plot_from_yaml_config_path_without_pyyaml(tmp_path: Path):
    output = tmp_path / "yaml-render.png"
    config_path = tmp_path / "plot.yaml"
    config_path.write_text(
        "\n".join(
            [
                "paper:",
                "  profile: icml",
                "  style: academic-muted",
                "figure:",
                "  template: bar.ablation",
                "  data:",
                "    component: [Full, w/o aug, w/o mixup]",
                "    score: [82.4, 80.1, 79.6]",
                "  x: component",
                "  y: score",
                f"  output: {output}",
                "  title: YAML Render",
            ]
        ),
        encoding="utf-8",
    )

    fig, ax, spec = plot_from_config(str(config_path))

    assert spec["template"]["name"] == "bar.ablation"
    assert ax.get_title() == "YAML Render"
    assert output.exists()
    fig.clf()


def test_managed_figure_closes_returned_figure():
    import matplotlib.pyplot as plt

    data = {
        "epoch": [1, 2, 3, 1, 2, 3],
        "acc": [70, 73, 75, 68, 71, 74],
        "method": ["A", "A", "A", "B", "B", "B"],
    }

    with managed_figure(
        plot(
            template="line.sota_compare",
            data=data,
            x="epoch",
            y="acc",
            hue="method",
        )
    ) as (fig, ax, spec):
        assert fig.number in plt.get_fignums()
        assert ax.get_xlabel() == "Epoch"
        assert spec["template"]["chart_type"] == "line"

    assert fig.number not in plt.get_fignums()


def test_cli_render_from_yaml_config(tmp_path: Path):
    output = tmp_path / "cli-render.png"
    config_path = tmp_path / "cli-plot.yaml"
    config_path.write_text(
        "\n".join(
            [
                "paper:",
                "  profile: neurips",
                "  style: academic-bright",
                "figure:",
                "  template: line.training_curve",
                "  data:",
                "    epoch: [1, 2, 3, 1, 2, 3]",
                "    acc: [70, 73, 75, 68, 71, 74]",
                "    method: [A, A, A, B, B, B]",
                "  x: epoch",
                "  y: acc",
                "  hue: method",
                f"  output: {output}",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "render", str(config_path)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert str(output) in result.stdout
    assert output.exists()


def test_cli_render_directory_of_configs(tmp_path: Path):
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    output_a = tmp_path / "a.png"
    output_b = tmp_path / "b.png"

    (config_dir / "a.yaml").write_text(
        "\n".join(
            [
                "paper:",
                "  profile: icml",
                "  style: academic-muted",
                "figure:",
                "  template: bar.ablation",
                "  data:",
                "    component: [Full, w/o aug]",
                "    score: [82.4, 80.1]",
                "  x: component",
                "  y: score",
                f"  output: {output_a}",
            ]
        ),
        encoding="utf-8",
    )
    (config_dir / "b.yaml").write_text(
        "\n".join(
            [
                "paper:",
                "  profile: neurips",
                "  style: academic-bright",
                "figure:",
                "  template: hist.default",
                "  data:",
                "    error: [-1.0, -0.5, 0.0, 0.5, 1.0]",
                "  x: error",
                f"  output: {output_b}",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "render", str(config_dir)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert str(output_a) in result.stdout
    assert str(output_b) in result.stdout
    assert output_a.exists()
    assert output_b.exists()


def test_cli_color_advisor_exports_mapping(tmp_path: Path):
    export_path = tmp_path / "advisor-map.json"
    persist_path = tmp_path / "paper-colors.json"
    config_path = tmp_path / "advisor.yaml"
    config_path.write_text(
        "\n".join(
            [
                "paper:",
                "  profile: icml",
                "  style: academic-muted",
                "  color_advisor:",
                "    enabled: true",
                "    usage: manuscript",
                "    tone: restrained",
                "    namespace: paper-a",
                f"    persist_path: {persist_path}",
                "    preferred_order: [Ours, Baseline]",
                "figure:",
                "  template: line.sota_compare",
                "  data:",
                "    epoch: [1, 2, 1, 2]",
                "    acc: [80, 82, 77, 79]",
                "    method: [Baseline, Baseline, Ours, Ours]",
                "  x: epoch",
                "  y: acc",
                "  hue: method",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paperplot.cli",
            "color-advisor",
            str(config_path),
            "--export-map",
            str(export_path),
        ],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    exported = json.loads(export_path.read_text(encoding="utf-8"))

    assert payload["recommendation"]["template"]["chart_type"] == "line-plot"
    assert payload["series"]["Ours"] != payload["series"]["Baseline"]
    assert exported["namespace"] == "paper-a"


def test_plot_from_yaml_composite_layout(tmp_path: Path):
    output = tmp_path / "report-layout.png"
    config_path = tmp_path / "report-layout.yaml"
    config_path.write_text(
        "\n".join(
            [
                "paper:",
                "  profile: emnlp",
                "  style: nature-clean",
                "figure:",
                "  template: table_mix.default",
                "  data:",
                "    placeholder: [1]",
                f"  output: {output}",
                "  elements:",
                "    - template: table.default",
                "      title: Summary Table",
                "      row: 0",
                "      col: 0",
                "      data:",
                "        - {Model: A, F1: 81.2}",
                "        - {Model: B, F1: 82.7}",
                "    - template: bar.default",
                "      title: F1 Score",
                "      row: 0",
                "      col: 1",
                "      data:",
                "        model: [A, B]",
                "        score: [81.2, 82.7]",
                "      x: model",
                "      y: score",
            ]
        ),
        encoding="utf-8",
    )

    fig, axes, spec = plot_from_config(str(config_path))

    assert spec["template"]["name"] == "table_mix.default"
    assert len(axes) == 2
    assert output.exists()
    fig.clf()


def test_scatter_grouped_bar_heatmap_radar_and_composite_layouts(tmp_path: Path):
    scatter_output = tmp_path / "scatter.png"
    grouped_output = tmp_path / "grouped.png"
    heatmap_output = tmp_path / "heatmap.png"
    radar_output = tmp_path / "radar.png"
    subplot_output = tmp_path / "subplots.png"
    mixed_output = tmp_path / "mixed.png"

    scatter_fig, scatter_ax, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "scatter.default",
                "data": {
                    "dim1": [1, 2, 3, 4, 1.5, 2.5, 3.5],
                    "dim2": [2, 3, 2.5, 4, 1.2, 2.2, 3.2],
                    "cluster": ["A", "A", "A", "A", "B", "B", "B"],
                },
                "x": "dim1",
                "y": "dim2",
                "hue": "cluster",
                "output": str(scatter_output),
            },
        }
    )
    assert scatter_output.exists()
    assert scatter_ax.get_xlabel() == "Dim1"
    scatter_fig.clf()

    grouped_fig, grouped_ax, grouped_spec = plot_from_config(
        {
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
                "output": str(grouped_output),
            },
        }
    )
    assert grouped_spec["template"]["name"] == "ablation.study"
    assert grouped_output.exists()
    grouped_fig.clf()

    heatmap_fig, _, _ = plot_from_config(
        {
            "paper": {"profile": "acl", "style": "academic-muted"},
            "figure": {
                "template": "heatmap.default",
                "data": {
                    "matrix": [[0.92, 0.75, 0.61], [0.71, 0.88, 0.67], [0.64, 0.69, 0.91]],
                    "x_labels": ["Model A", "Model B", "Model C"],
                    "y_labels": ["Dataset 1", "Dataset 2", "Dataset 3"],
                },
                "output": str(heatmap_output),
                "annotate": True,
            },
        }
    )
    assert heatmap_output.exists()
    heatmap_fig.clf()

    radar_fig, radar_ax, _ = plot_from_config(
        {
            "paper": {"profile": "cvpr", "style": "grayscale-safe"},
            "figure": {
                "template": "radar.default",
                "data": {
                    "categories": ["Acc", "Robust", "Speed", "Memory", "Calib"],
                    "series": [
                        {"label": "PaperPlot", "values": [0.88, 0.81, 0.72, 0.68, 0.79]},
                        {"label": "Baseline", "values": [0.83, 0.74, 0.76, 0.71, 0.69]},
                    ],
                },
                "output": str(radar_output),
            },
        }
    )
    assert radar_ax.name == "polar"
    assert radar_output.exists()
    radar_fig.clf()

    subplot_fig, subplot_axes, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "subplots.default",
                "data": {"unused": [1]},
                "output": str(subplot_output),
                "panels": [
                    {
                        "template": "line.training_curve",
                        "data": {"epoch": [1, 2, 3], "acc": [70, 73, 75]},
                        "x": "epoch",
                        "y": "acc",
                        "title": "Curve",
                    },
                    {
                        "template": "hist.default",
                        "data": {"error": [-1.0, -0.2, 0.1, 0.3, 0.9]},
                        "x": "error",
                        "title": "Histogram",
                    },
                ],
            },
        }
    )
    assert subplot_output.exists()
    assert len(subplot_axes.flatten()) >= 2
    subplot_fig.clf()

    mixed_fig, mixed_axes, _ = plot_from_config(
        {
            "paper": {"profile": "emnlp", "style": "nature-clean"},
            "figure": {
                "template": "table_mix.default",
                "data": {"unused": [1]},
                "output": str(mixed_output),
                "elements": [
                    {
                        "template": "table.default",
                        "data": [
                            {"Model": "A", "F1": 81.2},
                            {"Model": "B", "F1": 82.7},
                        ],
                        "title": "Summary Table",
                        "row": 0,
                        "col": 0,
                    },
                    {
                        "template": "bar.default",
                        "data": {"model": ["A", "B"], "score": [81.2, 82.7]},
                        "x": "model",
                        "y": "score",
                        "title": "Bar View",
                        "row": 0,
                        "col": 1,
                    },
                ],
            },
        }
    )
    assert mixed_output.exists()
    assert len(mixed_axes) == 2
    mixed_fig.clf()


def test_uncertainty_annotations_for_line_bar_and_scatter(tmp_path: Path):
    line_output = tmp_path / "line_ci.png"
    bar_output = tmp_path / "bar_err.png"
    scatter_output = tmp_path / "scatter_err.png"

    line_fig, line_ax, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "line.sota_compare",
                "data": {
                    "epoch": [1, 2, 3],
                    "acc": [70, 73, 75],
                    "lower": [68.8, 71.9, 73.5],
                    "upper": [71.2, 74.1, 76.5],
                },
                "x": "epoch",
                "y": "acc",
                "y_lower": "lower",
                "y_upper": "upper",
                "output": str(line_output),
            },
        }
    )
    assert line_output.exists()
    assert len(line_ax.collections) >= 1
    line_fig.clf()

    bar_fig, bar_ax, _ = plot_from_config(
        {
            "paper": {"profile": "neurips", "style": "academic-bright"},
            "figure": {
                "template": "bar.default",
                "data": {
                    "model": ["A", "B", "C"],
                    "score": [81.2, 82.5, 80.9],
                    "err": [0.4, 0.3, 0.5],
                },
                "x": "model",
                "y": "score",
                "yerr": "err",
                "annotations": [{"x1": "A", "x2": "B", "text": "**"}],
                "output": str(bar_output),
            },
        }
    )
    assert bar_output.exists()
    assert len(bar_ax.patches) == 3
    assert len(bar_ax.texts) >= 1
    bar_fig.clf()

    scatter_fig, scatter_ax, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "scatter.default",
                "data": {
                    "xv": [1.0, 2.0, 3.0],
                    "yv": [2.0, 2.5, 3.1],
                    "xerr": [0.1, 0.15, 0.08],
                    "yerr": [0.2, 0.12, 0.18],
                },
                "x": "xv",
                "y": "yv",
                "xerr": "xerr",
                "yerr": "yerr",
                "output": str(scatter_output),
            },
        }
    )
    assert scatter_output.exists()
    assert len(scatter_ax.collections) >= 1
    scatter_fig.clf()


def test_subplots_shared_axes_and_global_legend(tmp_path: Path):
    output = tmp_path / "subplots_shared.png"
    fig, axes, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "subplots.default",
                "data": {"unused": [1]},
                "output": str(output),
                "panels": [
                    {
                        "template": "line.sota_compare",
                        "data": {
                            "epoch": [1, 2, 3, 1, 2, 3],
                            "acc": [70, 73, 75, 68, 71, 74],
                            "method": ["A", "A", "A", "B", "B", "B"],
                        },
                        "x": "epoch",
                        "y": "acc",
                        "hue": "method",
                        "title": "Panel 1",
                    },
                    {
                        "template": "line.sota_compare",
                        "data": {
                            "epoch": [1, 2, 3, 1, 2, 3],
                            "acc": [72, 74, 76, 69, 72, 75],
                            "method": ["A", "A", "A", "B", "B", "B"],
                        },
                        "x": "epoch",
                        "y": "acc",
                        "hue": "method",
                        "title": "Panel 2",
                    },
                ],
                "ncols": 2,
                "sharey": True,
                "global_legend": True,
                "panel_labels": "auto",
                "figure_note": "Results averaged over 3 seeds.",
            },
        }
    )
    assert output.exists()
    assert fig.legends
    assert axes[0][1].get_ylabel() == ""
    assert any(text.get_text() == "(a)" for text in axes[0][0].texts)
    assert any("Results averaged over 3 seeds." == text.get_text() for text in fig.texts)
    fig.clf()


def test_grouped_bar_significance_annotation(tmp_path: Path):
    output = tmp_path / "grouped_sig.png"
    fig, ax, _ = plot_from_config(
        {
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
                "annotations": [{"x1": ["Encoder", "Base"], "x2": ["Encoder", "Removed"], "text": "p<0.01"}],
                "output": str(output),
            },
        }
    )
    assert output.exists()
    assert any("p<0.01" == text.get_text() for text in ax.texts)
    fig.clf()


def test_declarative_significance_for_bar_and_grouped_bar(tmp_path: Path):
    bar_output = tmp_path / "bar_sig_decl.png"
    grouped_output = tmp_path / "grouped_sig_decl.png"

    bar_fig, bar_ax, _ = plot_from_config(
        {
            "paper": {"profile": "neurips", "style": "academic-bright"},
            "figure": {
                "template": "bar.default",
                "data": {
                    "model": ["A", "B", "C"],
                    "score": [81.2, 82.5, 80.9],
                },
                "x": "model",
                "y": "score",
                "significance": [{"compare": ["A", "B"], "text": "*"}],
                "output": str(bar_output),
            },
        }
    )
    assert bar_output.exists()
    assert any("*" == text.get_text() for text in bar_ax.texts)
    bar_fig.clf()

    grouped_fig, grouped_ax, _ = plot_from_config(
        {
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
                "significance": [
                    {
                        "compare": [["Encoder", "Base"], ["Encoder", "Removed"]],
                        "text": "p<0.01",
                    }
                ],
                "output": str(grouped_output),
            },
        }
    )
    assert grouped_output.exists()
    assert any("p<0.01" == text.get_text() for text in grouped_ax.texts)
    grouped_fig.clf()


def test_grouped_bar_significance_within_each_category(tmp_path: Path):
    output = tmp_path / "grouped_sig_within_each.png"
    fig, ax, _ = plot_from_config(
        {
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
                "significance": [
                    {
                        "within": "each",
                        "pairs": [["Base", "Removed"]],
                        "text": "p<0.05",
                    }
                ],
                "output": str(output),
            },
        }
    )
    assert output.exists()
    assert sum(text.get_text() == "p<0.05" for text in ax.texts) == 2
    fig.clf()


def test_bar_significance_against_baseline_with_exclude(tmp_path: Path):
    output = tmp_path / "bar_sig_against.png"
    fig, ax, _ = plot_from_config(
        {
            "paper": {"profile": "neurips", "style": "academic-bright"},
            "figure": {
                "template": "bar.default",
                "data": {
                    "model": ["Base", "Lite", "Large", "Oracle"],
                    "score": [81.2, 80.5, 82.7, 84.1],
                },
                "x": "model",
                "y": "score",
                "significance": [
                    {
                        "within": "all",
                        "against": "Base",
                        "exclude": ["Oracle"],
                        "text": ["ns", "**"],
                    }
                ],
                "output": str(output),
            },
        }
    )
    assert output.exists()
    labels = [text.get_text() for text in ax.texts]
    assert "ns" in labels
    assert "**" in labels
    assert "Oracle" not in labels
    fig.clf()


def test_axis_formatters_and_panel_captions(tmp_path: Path):
    output = tmp_path / "formatters.png"
    fig, axes, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "subplots.default",
                "data": {"unused": [1]},
                "output": str(output),
                "ncols": 2,
                "panels": [
                    {
                        "template": "bar.default",
                        "data": {"model": ["A", "B"], "score": [0.812, 0.827]},
                        "x": "model",
                        "y": "score",
                        "yformatter": "percent",
                        "caption": "Normalized scores.",
                    },
                    {
                        "template": "bar.default",
                        "data": {"model": ["A", "B"], "score": [1250, 2125000]},
                        "x": "model",
                        "y": "score",
                        "yformatter": "compact",
                        "caption": "Parameter counts.",
                    },
                ],
            },
        }
    )
    assert output.exists()
    assert "%" in axes[0][0].yaxis.get_major_formatter()(0.5, 0)
    assert "K" in axes[0][1].yaxis.get_major_formatter()(1250, 0)
    assert any("Normalized scores." == text.get_text() for text in axes[0][0].texts)
    fig.clf()


def test_scatter_pareto_frontier_labels_and_log_scaling(tmp_path: Path):
    scatter_output = tmp_path / "pareto.png"
    line_output = tmp_path / "scaling.png"

    scatter_fig, scatter_ax, _ = plot_from_config(
        {
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
                "output": str(scatter_output),
            },
        }
    )
    assert scatter_output.exists()
    assert any(text.get_text() == "Mip-Splatting" for text in scatter_ax.texts)
    assert any(line.get_linestyle() == "--" for line in scatter_ax.lines)
    scatter_fig.clf()

    line_fig, line_ax, _ = plot_from_config(
        {
            "paper": {"profile": "icml", "style": "academic-muted"},
            "figure": {
                "template": "line.scaling_law",
                "data": {
                    "tokens": [10_000_000, 30_000_000, 100_000_000],
                    "loss": [2.5, 2.3, 2.1],
                },
                "x": "tokens",
                "y": "loss",
                "xscale": "log",
                "output": str(line_output),
            },
        }
    )
    assert line_output.exists()
    assert line_ax.get_xscale() == "log"
    line_fig.clf()
