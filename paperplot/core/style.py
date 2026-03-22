"""Matplotlib style application."""

from __future__ import annotations

from typing import Any, Mapping

from paperplot.core.config import resolve_figure_spec
from paperplot.core.mpl import prepare_matplotlib_env


def build_rcparams(spec: Mapping[str, Any]) -> dict[str, Any]:
    axes = spec.get("axes", {})
    grid = axes.get("grid", False)
    grid_alpha = axes.get("grid_alpha", 0.2)
    legend = spec.get("legend", {})
    lines = spec.get("lines", {})
    font = spec.get("font", {})
    figure = spec.get("figure", {})

    rc = {
        "axes.grid": grid,
        "grid.alpha": grid_alpha,
        "grid.linewidth": axes.get("grid_linewidth", 0.6),
        "grid.linestyle": axes.get("grid_linestyle", "-"),
        "axes.axisbelow": True,
        "axes.spines.top": axes.get("spines_top", False),
        "axes.spines.right": axes.get("spines_right", False),
        "axes.linewidth": axes.get("linewidth", 0.9),
        "axes.edgecolor": axes.get("edgecolor", "#222222"),
        "legend.frameon": legend.get("frameon", False),
        "legend.loc": legend.get("loc", "best"),
        "legend.fontsize": legend.get("fontsize", font.get("tick_size", 9)),
        "legend.title_fontsize": legend.get("title_fontsize", font.get("tick_size", 9)),
        "legend.handlelength": legend.get("handlelength", 1.8),
        "lines.linewidth": lines.get("linewidth", 2.0),
        "lines.markersize": lines.get("markersize", 6),
        "lines.markeredgewidth": lines.get("markeredgewidth", 0.8),
        "figure.figsize": figure["figsize"],
        "figure.dpi": spec.get("export", {}).get("dpi", 300),
        "figure.facecolor": figure.get("facecolor", "white"),
        "savefig.facecolor": figure.get("facecolor", "white"),
        "font.family": font.get("family", "serif"),
        "font.size": font.get("size", 10),
        "axes.titlesize": font.get("title_size", font.get("size", 10)),
        "axes.labelsize": font.get("label_size", font.get("size", 10)),
        "xtick.labelsize": font.get("tick_size", font.get("size", 9)),
        "ytick.labelsize": font.get("tick_size", font.get("size", 9)),
        "xtick.direction": axes.get("tick_direction", "out"),
        "ytick.direction": axes.get("tick_direction", "out"),
        "xtick.major.size": axes.get("tick_size", 3.5),
        "ytick.major.size": axes.get("tick_size", 3.5),
        "xtick.major.width": axes.get("tick_width", 0.8),
        "ytick.major.width": axes.get("tick_width", 0.8),
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,
        "mathtext.fontset": font.get("mathtext_fontset", "dejavuserif"),
    }

    palette = spec.get("palette", {}).get("colors")
    if palette:
        prepare_matplotlib_env()
        import matplotlib.pyplot as plt

        rc["axes.prop_cycle"] = plt.cycler(color=palette)
    return rc


def use_style(
    *,
    profile: str | None = None,
    visual: str | None = None,
    size: str | None = None,
    override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve and apply a PaperPlot style to Matplotlib."""
    prepare_matplotlib_env()
    import matplotlib as mpl

    spec = resolve_figure_spec(
        template="line.default",
        profile=profile,
        visual=visual,
        size=size,
        override=override,
    )
    mpl.rcParams.update(build_rcparams(spec))
    return spec
