"""Template-driven figure rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from paperplot.core.config import load_plot_config, resolve_figure_spec, resolve_template
from paperplot.core.io import extract_series, load_data
from paperplot.core.mpl import prepare_matplotlib_env
from paperplot.core.save import save_figure
from paperplot.core.style import build_rcparams
from paperplot.plots.formatting import apply_axis_formatters
from paperplot.registry.api import get_plotter


def plot(
    *,
    template: str,
    data: Any,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    profile: str | None = None,
    visual: str | None = None,
    size: str | None = None,
    output: str | None = None,
    override: Mapping[str, Any] | None = None,
    **kwargs: Any,
):
    """Render a figure from a registered template."""
    return render_template(
        template=template,
        data=data,
        x=x,
        y=y,
        hue=hue,
        profile=profile,
        visual=visual,
        size=size,
        output=output,
        override=override,
        **kwargs,
    )


def render_template(
    *,
    template: str,
    data: Any,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
    profile: str | None = None,
    visual: str | None = None,
    size: str | None = None,
    output: str | None = None,
    override: Mapping[str, Any] | None = None,
    **kwargs: Any,
):
    spec = resolve_figure_spec(
        template=template,
        profile=profile,
        visual=visual,
        size=size,
        override=override,
    )
    template_spec = spec["template"]
    prepare_matplotlib_env()
    import matplotlib.pyplot as plt

    plot_data = load_data(data)

    with plt.rc_context(build_rcparams(spec)):
        fig, ax = plt.subplots(figsize=spec["figure"]["figsize"])
        if template_spec["chart_type"] == "radar":
            fig.clf()
            ax = fig.add_subplot(111, projection="polar")
        result_ax = _dispatch_plot(
            fig=fig,
            ax=ax,
            plot_data=plot_data,
            template_spec=template_spec,
            spec=spec,
            x=x,
            y=y,
            hue=hue,
            kwargs=kwargs,
        )

        if output:
            save_figure(fig, output, spec.get("export", {}))
        return fig, result_ax, spec


def plot_from_config(config: str | Path | Mapping[str, Any]):
    """Render a figure from a PaperPlot config mapping or YAML file."""
    payload = load_plot_config(config)
    paper = payload.get("paper", {})
    figure = payload.get("figure", {})

    if not isinstance(paper, Mapping):
        raise TypeError("'paper' section must be a mapping when present.")
    if not isinstance(figure, Mapping):
        raise TypeError("'figure' section must be a mapping.")

    template = figure.get("template")
    data = figure.get("data")
    if template is None:
        raise ValueError("Figure config must define 'template'.")
    if data is None:
        raise ValueError("Figure config must define 'data'.")

    forwarded = {
        key: value
        for key, value in figure.items()
        if key
        not in {
            "template",
            "data",
            "x",
            "y",
            "hue",
            "size",
            "output",
            "override",
        }
    }

    return plot(
        template=template,
        data=data,
        x=figure.get("x"),
        y=figure.get("y"),
        hue=figure.get("hue"),
        profile=paper.get("profile"),
        visual=paper.get("style"),
        size=figure.get("size"),
        output=figure.get("output"),
        override=figure.get("override"),
        **forwarded,
    )


def _dispatch_plot(
    *,
    fig: Any,
    ax: Any,
    plot_data: Any,
    template_spec: dict[str, Any],
    spec: dict[str, Any],
    x: str | None,
    y: str | None,
    hue: str | None,
    kwargs: Mapping[str, Any],
):
    chart_type = template_spec["chart_type"]
    if chart_type == "subplots":
        return _render_subplots(
            fig=fig,
            spec=spec,
            template_spec=template_spec,
            panels=kwargs.get("panels"),
            options=kwargs,
        )
    if chart_type == "table_mix":
        return _render_table_mix(
            fig=fig,
            spec=spec,
            template_spec=template_spec,
            elements=kwargs.get("elements"),
            options=kwargs,
        )

    plotter = get_plotter(chart_type)
    required = template_spec.get("mappings", {}).get("required", [])
    missing = [field for field in required if {"x": x, "y": y, "hue": hue}.get(field) is None]
    if missing:
        raise ValueError(f"Missing required template mappings: {missing}")

    plotter(
        fig=fig,
        ax=ax,
        data=plot_data,
        x=extract_series(plot_data, x),
        y=extract_series(plot_data, y),
        hue=extract_series(plot_data, hue) if hue else None,
        spec=spec,
        template=template_spec,
        x_key=x,
        y_key=y,
        hue_key=hue,
        **kwargs,
    )
    apply_axis_formatters(
        ax=ax,
        xformatter=kwargs.get("xformatter"),
        yformatter=kwargs.get("yformatter"),
        xscale=kwargs.get("xscale"),
        yscale=kwargs.get("yscale"),
    )
    return ax


def _render_subplots(*, fig: Any, spec: dict[str, Any], template_spec: dict[str, Any], panels: Any, options: Mapping[str, Any]):
    if not isinstance(panels, list) or not panels:
        raise ValueError("Subplots layouts require a non-empty 'panels' list.")
    fig.clf()
    layout = template_spec.get("layout", {})
    defaults = template_spec.get("defaults", {})
    nrows = int(options.get("nrows", layout.get("nrows", defaults.get("nrows", 1))))
    ncols = int(options.get("ncols", layout.get("ncols", defaults.get("ncols", len(panels)))))
    figure_title = options.get("figure_title", defaults.get("figure_title"))
    panel_labels = options.get("panel_labels", defaults.get("panel_labels"))
    sharex = bool(options.get("sharex", defaults.get("sharex", False)))
    sharey = bool(options.get("sharey", defaults.get("sharey", False)))
    global_legend = bool(options.get("global_legend", defaults.get("global_legend", False)))
    axes = fig.subplots(nrows=nrows, ncols=ncols, squeeze=False, sharex=sharex, sharey=sharey)
    flat_axes = [axis for row in axes for axis in row]
    if len(panels) > len(flat_axes):
        raise ValueError("Subplots layout does not have enough axes for the provided panels.")

    for index, (axis, panel) in enumerate(zip(flat_axes, panels, strict=False)):
        _render_panel(axis=axis, fig=fig, spec=spec, panel=panel)
        label = panel.get("panel_label") or _resolve_panel_label(panel_labels, index)
        if label:
            axis.text(-0.12, 1.08, label, transform=axis.transAxes, fontsize=10, fontweight="bold", va="top")
        caption = panel.get("caption")
        if caption:
            axis.text(0.5, -0.22, str(caption), transform=axis.transAxes, ha="center", va="top", fontsize=8)
    for axis in flat_axes[len(panels) :]:
        axis.axis("off")
    if sharex or sharey:
        _simplify_shared_axes(axes, sharex=sharex, sharey=sharey)
    if global_legend:
        _apply_global_legend(fig, flat_axes[: len(panels)])
    if figure_title:
        fig.suptitle(figure_title, y=1.02, fontsize=11)
    figure_note = options.get("figure_note", defaults.get("figure_note"))
    if figure_note:
        fig.text(0.5, 0.01, str(figure_note), ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return axes


def _render_table_mix(*, fig: Any, spec: dict[str, Any], template_spec: dict[str, Any], elements: Any, options: Mapping[str, Any]):
    if not isinstance(elements, list) or not elements:
        raise ValueError("Table/figure layouts require a non-empty 'elements' list.")
    fig.clf()
    layout = template_spec.get("layout", {})
    defaults = template_spec.get("defaults", {})
    nrows = options.get("nrows", layout.get("nrows", 1))
    ncols = options.get("ncols", layout.get("ncols", len(elements)))
    width_ratios = options.get("width_ratios", layout.get("width_ratios"))
    height_ratios = options.get("height_ratios", layout.get("height_ratios"))
    figure_title = options.get("figure_title", defaults.get("figure_title"))
    global_legend = bool(options.get("global_legend", defaults.get("global_legend", False)))
    panel_labels = options.get("panel_labels", defaults.get("panel_labels"))
    gridspec = fig.add_gridspec(nrows, ncols, width_ratios=width_ratios, height_ratios=height_ratios)

    axes: list[Any] = []
    for index, element in enumerate(elements):
        row = element.get("row", index // ncols)
        col = element.get("col", index % ncols)
        rowspan = element.get("rowspan", 1)
        colspan = element.get("colspan", 1)
        axis = fig.add_subplot(gridspec[row : row + rowspan, col : col + colspan], projection="polar" if element.get("projection") == "polar" else None)
        axes.append(axis)
        _render_panel(axis=axis, fig=fig, spec=spec, panel=element)
        label = element.get("panel_label") or _resolve_panel_label(panel_labels, index)
        if label:
            axis.text(-0.12, 1.08, label, transform=axis.transAxes, fontsize=10, fontweight="bold", va="top")
        caption = element.get("caption")
        if caption:
            axis.text(0.5, -0.22, str(caption), transform=axis.transAxes, ha="center", va="top", fontsize=8)
    if global_legend:
        _apply_global_legend(fig, axes)
    if figure_title:
        fig.suptitle(figure_title, y=1.02, fontsize=11)
    figure_note = options.get("figure_note", defaults.get("figure_note"))
    if figure_note:
        fig.text(0.5, 0.01, str(figure_note), ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return axes


def _render_panel(*, axis: Any, fig: Any, spec: dict[str, Any], panel: Mapping[str, Any]) -> None:
    template_name = panel.get("template")
    if not template_name:
        raise ValueError("Each panel requires a 'template'.")
    panel_template = resolve_template(template_name)
    panel_data = load_data(panel.get("data"))
    x_key = panel.get("x")
    y_key = panel.get("y")
    hue_key = panel.get("hue")
    panel_kwargs = {
        key: value
        for key, value in panel.items()
        if key not in {"template", "data", "x", "y", "hue", "row", "col", "rowspan", "colspan", "projection"}
    }
    plotter = get_plotter(panel_template["chart_type"])
    required = panel_template.get("mappings", {}).get("required", [])
    missing = [field for field in required if {"x": x_key, "y": y_key, "hue": hue_key}.get(field) is None]
    if missing:
        raise ValueError(f"Missing required panel mappings: {missing}")
    if panel_template["chart_type"] == "radar" and getattr(axis, "name", "") != "polar":
        subplotspec = axis.get_subplotspec()
        axis.remove()
        axis = fig.add_subplot(subplotspec, projection="polar")
    plotter(
        fig=fig,
        ax=axis,
        data=panel_data,
        x=extract_series(panel_data, x_key),
        y=extract_series(panel_data, y_key),
        hue=extract_series(panel_data, hue_key) if hue_key else None,
        spec=spec,
        template=panel_template,
        x_key=x_key,
        y_key=y_key,
        hue_key=hue_key,
        **panel_kwargs,
    )
    apply_axis_formatters(
        ax=axis,
        xformatter=panel_kwargs.get("xformatter"),
        yformatter=panel_kwargs.get("yformatter"),
    )


def _apply_global_legend(fig: Any, axes: list[Any]) -> None:
    handles: list[Any] = []
    labels: list[str] = []
    for axis in axes:
        axis_handles, axis_labels = axis.get_legend_handles_labels()
        for handle, label in zip(axis_handles, axis_labels, strict=False):
            if label and label not in labels:
                handles.append(handle)
                labels.append(label)
        legend = axis.get_legend()
        if legend is not None:
            legend.remove()
    if handles:
        fig.legend(handles, labels, loc="upper center", ncol=max(1, min(len(labels), 4)), frameon=False, bbox_to_anchor=(0.5, 1.02))


def _simplify_shared_axes(axes: Any, *, sharex: bool, sharey: bool) -> None:
    nrows, ncols = axes.shape
    for row_index in range(nrows):
        for col_index in range(ncols):
            axis = axes[row_index][col_index]
            if sharex and row_index < nrows - 1:
                axis.tick_params(labelbottom=False)
                axis.set_xlabel("")
            if sharey and col_index > 0:
                axis.tick_params(labelleft=False)
                axis.set_ylabel("")


def _resolve_panel_label(panel_labels: Any, index: int) -> str | None:
    if panel_labels == "auto":
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        if index < len(alphabet):
            return f"({alphabet[index]})"
    if isinstance(panel_labels, list) and index < len(panel_labels):
        return panel_labels[index]
    return None
