import json
import os
import subprocess
import sys

from paperplot.core.config import resolve_figure_spec, resolve_template
from paperplot.profiles import PROFILES
from paperplot.styles import STYLES
from paperplot.templates import TEMPLATES
from paperplot.registry.api import (
    autoload_project_assets,
    get_profile,
    get_style,
    get_template,
    register_template,
)


def test_resolve_template_inherits_from_base():
    register_template(
        "line.custom",
        {
            "base": "line.sota_compare",
            "defaults": {"marker": False},
        },
    )

    template = resolve_template("line.custom")
    assert template["chart_type"] == "line"
    assert template["defaults"]["marker"] is False
    assert template["layout"]["size_token"] == "single"


def test_dotted_override_updates_nested_config():
    spec = resolve_figure_spec(
        template="line.default",
        override={"lines.linewidth": 3.4, "axes.grid": True},
    )

    assert spec["lines"]["linewidth"] == 3.4
    assert spec["axes"]["grid"] is True


def test_color_advisor_resolves_line_palette():
    spec = resolve_figure_spec(
        template="line.default",
        color_advisor={
            "enabled": True,
            "usage": "manuscript",
            "tone": "restrained",
            "series_count": 2,
        },
        override={
            "axes.grid": True,
        },
    )

    advisor = spec["palette"]["advisor"]
    assert advisor["template"]["chart_type"] == "line-plot"
    assert spec["palette"]["colors"][0] != "#4C78A8"
    assert len(spec["palette"]["colors"]) >= 4
    assert advisor["template"]["id"] == "editorial-lines-light"


def test_color_advisor_resolves_diverging_heatmap_palette():
    spec = resolve_figure_spec(
        template="heatmap.default",
        color_advisor={
            "enabled": True,
            "usage": "manuscript",
        },
        override={
            "template.defaults.cmap": "RdBu",
        },
    )

    assert spec["palette"]["advisor"]["template"]["palette_class"] == "diverging"
    assert len(spec["palette"]["cmap_colors"]) == 9


def test_builtin_profiles_are_exposed_from_profiles_package():
    assert set(PROFILES) == {"icml", "neurips", "acl", "cvpr", "emnlp", "nature"}
    assert PROFILES["icml"]["sizes"]["single"] == [3.25, 2.2]
    assert PROFILES["nature"]["font"]["family"] == "sans-serif"


def test_builtin_styles_are_exposed_from_styles_package():
    assert set(STYLES) == {
        "default",
        "academic-muted",
        "academic-bright",
        "grayscale-safe",
        "nature-clean",
    }
    assert STYLES["default"]["axes"]["spines_right"] is False
    assert STYLES["grayscale-safe"]["base"] == "default"


def test_builtin_templates_are_exposed_from_templates_package():
    assert set(TEMPLATES) == {
        "ablation.study",
        "line.default",
        "line.scaling_law",
        "line.sota_compare",
        "line.training_curve",
        "scatter.default",
        "scatter.pareto_frontier",
        "bar.default",
        "bar.ablation",
        "grouped_bar.default",
        "grouped_bar.benchmark_compare",
        "hist.default",
        "box.default",
        "box.distribution_compare",
        "heatmap.default",
        "heatmap.benchmark_matrix",
        "radar.default",
        "table.default",
        "subplots.default",
        "table_mix.default",
        "table_mix.paper_summary",
    }
    assert TEMPLATES["line.default"]["chart_type"] == "line"
    assert TEMPLATES["bar.ablation"]["base"] == "bar.default"


def test_autoload_project_assets_from_json_files(tmp_path):
    assets_dir = tmp_path / "paperplot_assets"
    (assets_dir / "profiles").mkdir(parents=True)
    (assets_dir / "styles").mkdir(parents=True)
    (assets_dir / "templates").mkdir(parents=True)

    (assets_dir / "profiles" / "lab.json").write_text(
        json.dumps(
            {
                "name": "lab",
                "font": {"family": "serif", "size": 9, "title_size": 9, "label_size": 9, "tick_size": 8},
                "sizes": {"single": [3.0, 2.0], "double": [6.4, 3.0], "square": [3.0, 3.0]},
                "export": {"formats": ["png"], "dpi": 200, "bbox_inches": "tight", "transparent": False},
            }
        ),
        encoding="utf-8",
    )
    (assets_dir / "styles" / "lab-muted.json").write_text(
        json.dumps(
            {
                "name": "lab-muted",
                "base": "default",
                "palette": {"colors": ["#111111", "#666666", "#AAAAAA"]},
            }
        ),
        encoding="utf-8",
    )
    (assets_dir / "templates" / "bar.lab.json").write_text(
        json.dumps(
            {
                "name": "bar.lab",
                "base": "bar.default",
                "defaults": {"sort": True, "title": "Lab Template"},
            }
        ),
        encoding="utf-8",
    )

    loaded = autoload_project_assets(tmp_path)

    assert loaded == {
        "profiles": ["lab"],
        "styles": ["lab-muted"],
        "templates": ["bar.lab"],
    }
    assert get_profile("lab")["sizes"]["single"] == [3.0, 2.0]
    assert get_style("lab-muted")["base"] == "default"
    assert get_template("bar.lab")["base"] == "bar.default"


def test_import_and_asset_autoload_do_not_emit_matplotlib_cache_warning(tmp_path):
    assets_dir = tmp_path / "paperplot_assets"
    (assets_dir / "profiles").mkdir(parents=True)
    (assets_dir / "profiles" / "lab.json").write_text(
        json.dumps(
            {
                "name": "lab",
                "font": {"family": "serif", "size": 9, "title_size": 9, "label_size": 9, "tick_size": 8},
                "sizes": {"single": [3.0, 2.0], "double": [6.4, 3.0], "square": [3.0, 3.0]},
                "export": {"formats": ["png"], "dpi": 200, "bbox_inches": "tight", "transparent": False},
            }
        ),
        encoding="utf-8",
    )

    command = [
        sys.executable,
        "-c",
        (
            "from paperplot import autoload_project_assets; "
            f"print(autoload_project_assets(r'{tmp_path}'))"
        ),
    ]
    env = dict(os.environ)
    env.pop("MPLCONFIGDIR", None)
    result = subprocess.run(command, capture_output=True, text=True, env=env, check=True)

    assert "Matplotlib created a temporary cache directory" not in result.stderr


def test_autoload_project_assets_from_yaml_files(tmp_path):
    assets_dir = tmp_path / ".paperplot"
    (assets_dir / "profiles").mkdir(parents=True)
    (assets_dir / "styles").mkdir(parents=True)
    (assets_dir / "templates").mkdir(parents=True)

    (assets_dir / "profiles" / "lab.yaml").write_text(
        "\n".join(
            [
                "name: lab-yaml",
                "font:",
                "  family: serif",
                "  size: 9",
                "  title_size: 9",
                "  label_size: 9",
                "  tick_size: 8",
                "sizes:",
                "  single: [3.1, 2.1]",
                "  double: [6.5, 3.0]",
                "  square: [3.0, 3.0]",
                "export:",
                "  formats: [png]",
                "  dpi: 220",
                "  bbox_inches: tight",
                "  transparent: false",
            ]
        ),
        encoding="utf-8",
    )
    (assets_dir / "styles" / "lab.yaml").write_text(
        "\n".join(
            [
                "name: lab-yaml-style",
                "base: default",
                "palette:",
                "  colors: [\"#111111\", \"#666666\"]",
            ]
        ),
        encoding="utf-8",
    )
    (assets_dir / "templates" / "bar.lab.yaml").write_text(
        "\n".join(
            [
                "name: bar.lab-yaml",
                "base: bar.default",
                "defaults:",
                "  sort: true",
                "  title: YAML Template",
            ]
        ),
        encoding="utf-8",
    )

    loaded = autoload_project_assets(tmp_path)

    assert loaded == {
        "profiles": ["lab-yaml"],
        "styles": ["lab-yaml-style"],
        "templates": ["bar.lab-yaml"],
    }
    assert get_profile("lab-yaml")["export"]["dpi"] == 220
    assert get_style("lab-yaml-style")["palette"]["colors"][0] == "#111111"
    assert get_template("bar.lab-yaml")["defaults"]["title"] == "YAML Template"


def test_cli_validate_config_and_assets(tmp_path):
    assets_dir = tmp_path / "paperplot_assets"
    (assets_dir / "styles").mkdir(parents=True)
    (assets_dir / "styles" / "lab.json").write_text(
        json.dumps({"name": "lab-validate", "base": "default"}),
        encoding="utf-8",
    )

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
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
            ]
        ),
        encoding="utf-8",
    )

    config_result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "validate-config", str(config_path)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )
    assets_result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "validate-assets", str(tmp_path)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert '"templates": ["bar.ablation"]' in config_result.stdout
    assert '"styles": ["lab-validate"]' in assets_result.stdout


def test_cli_legacy_validate_still_works(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
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
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "validate", str(config_path)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert '"templates": ["bar.ablation"]' in result.stdout


def test_validate_config_supports_color_advisor(tmp_path):
    config_path = tmp_path / "advisor-config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "paper:",
                "  profile: icml",
                "  style: academic-muted",
                "  color_advisor:",
                "    enabled: true",
                "    usage: manuscript",
                "figure:",
                "  template: line.sota_compare",
                "  data:",
                "    epoch: [1, 2, 1, 2]",
                "    acc: [80, 82, 77, 79]",
                "    method: [Ours, Ours, Baseline, Baseline]",
                "  x: epoch",
                "  y: acc",
                "  hue: method",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "validate-config", str(config_path)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert '"templates": ["line.sota_compare"]' in result.stdout


def test_cli_list_and_json_modes():
    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "--json", "list", "profiles"],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert '"icml"' in result.stdout
    assert '"neurips"' in result.stdout


def test_cli_quiet_mode_suppresses_stdout(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
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
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "--quiet", "validate-config", str(config_path)],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == ""


def test_cli_json_error_output_for_invalid_config():
    result = subprocess.run(
        [sys.executable, "-m", "paperplot.cli", "--json", "validate-config", "missing.yaml"],
        cwd="/root/PaperPlot",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert '"type": "FileNotFoundError"' in result.stderr
