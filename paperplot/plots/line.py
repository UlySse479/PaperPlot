"""Line plot implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import group_xy_by_hue, humanize_label, resolve_series_arg
from paperplot.plots.legends import apply_legends
from paperplot.core.color_advisor import resolve_series_color_map


def render_line(
    *,
    ax: Any,
    data: Any,
    x: list[Any] | None,
    y: list[Any] | None,
    hue: list[Any] | None,
    spec: dict[str, Any],
    template: dict[str, Any],
    x_key: str | None,
    y_key: str | None,
    hue_key: str | None,
    marker: bool | None = None,
    markers: list[Any] | None = None,
    linestyles: list[str] | None = None,
    legend: str | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    yerr: Any = None,
    y_lower: Any = None,
    y_upper: Any = None,
    xlim: list[float] | tuple[float, float] | None = None,
    ylim: list[float] | tuple[float, float] | None = None,
    xticks: list[Any] | None = None,
    yticks: list[Any] | None = None,
    legend_title: str | None = None,
    legend_bbox_to_anchor: list[float] | tuple[float, float] | None = None,
    legend_ncol: int | None = None,
    reference_lines: list[dict[str, Any]] | None = None,
    text_annotations: list[dict[str, Any]] | None = None,
    extra_legends: list[dict[str, Any]] | None = None,
    **_: Any,
) -> None:
    marker_enabled = template.get("defaults", {}).get("marker", True) if marker is None else marker
    legend_loc = legend or template.get("defaults", {}).get("legend_loc") or spec.get("legend", {}).get("loc", "best")
    markers = markers or template.get("defaults", {}).get("markers", ["o", "s", "^", "D", "P"])
    linestyles = linestyles or template.get("defaults", {}).get("linestyles", ["-", "--", "-.", ":"])
    yerr_values = resolve_series_arg(data, yerr)
    y_lower_values = resolve_series_arg(data, y_lower)
    y_upper_values = resolve_series_arg(data, y_upper)

    if hue is None:
        color_map = resolve_series_color_map(spec, [y_key or "series"])
        _plot_line_series(
            ax=ax,
            x_values=x or [],
            y_values=y or [],
            marker_style=markers[0] if marker_enabled else None,
            linestyle=linestyles[0],
            label=y_key,
            color=color_map.get(y_key or "series"),
            yerr_values=yerr_values,
            y_lower_values=y_lower_values,
            y_upper_values=y_upper_values,
        )
    else:
        grouped = group_xy_by_hue(x, y, hue)
        color_map = resolve_series_color_map(spec, list(grouped.keys()))
        for index, (group, series) in enumerate(grouped.items()):
            ordered = sorted(zip(series["x"], series["y"], strict=False), key=lambda item: item[0])
            _plot_line_series(
                ax=ax,
                x_values=[item[0] for item in ordered],
                y_values=[item[1] for item in ordered],
                marker_style=markers[index % len(markers)] if marker_enabled else None,
                linestyle=linestyles[index % len(linestyles)],
                label=str(group),
                color=color_map.get(group),
                yerr_values=_subset_series(yerr_values, hue, group),
                y_lower_values=_subset_series(y_lower_values, hue, group),
                y_upper_values=_subset_series(y_upper_values, hue, group),
            )
        apply_legends(
            ax=ax,
            loc=legend_loc,
            title=legend_title,
            bbox_to_anchor=legend_bbox_to_anchor,
            ncol=legend_ncol,
            extra_legends=extra_legends,
        )

    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    ax.margins(x=0.02, y=0.08)
    _apply_axis_overrides(ax=ax, xlim=xlim, ylim=ylim, xticks=xticks, yticks=yticks)
    _add_reference_lines(ax=ax, reference_lines=reference_lines)
    _add_text_annotations(ax=ax, text_annotations=text_annotations)
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)


def _plot_line_series(
    *,
    ax: Any,
    x_values: list[Any],
    y_values: list[Any],
    marker_style: Any,
    linestyle: str,
    label: str | None,
    color: str | None,
    yerr_values: Any,
    y_lower_values: Any,
    y_upper_values: Any,
) -> None:
    if yerr_values is not None:
        ax.errorbar(
            x_values,
            y_values,
            yerr=yerr_values,
            marker=marker_style,
            linestyle=linestyle,
            label=label,
            color=color,
            ecolor=color,
            clip_on=False,
            capsize=3,
        )
    else:
        ax.plot(
            x_values,
            y_values,
            marker=marker_style,
            linestyle=linestyle,
            label=label,
            color=color,
            clip_on=False,
        )
    if y_lower_values is not None and y_upper_values is not None:
        ax.fill_between(x_values, y_lower_values, y_upper_values, color=color, alpha=0.18)


def _subset_series(series: Any, hue: list[Any] | None, group: Any) -> Any:
    if series is None or hue is None:
        return series
    return [value for value, group_value in zip(series, hue, strict=False) if group_value == group]


def _apply_axis_overrides(
    *,
    ax: Any,
    xlim: list[float] | tuple[float, float] | None,
    ylim: list[float] | tuple[float, float] | None,
    xticks: list[Any] | None,
    yticks: list[Any] | None,
) -> None:
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)


def _add_reference_lines(*, ax: Any, reference_lines: list[dict[str, Any]] | None) -> None:
    if not reference_lines:
        return
    for line in reference_lines:
        if not isinstance(line, dict) or "y" not in line:
            continue
        ax.axhline(
            y=line["y"],
            color=line.get("color", "#888888"),
            linestyle=line.get("linestyle", "-"),
            linewidth=line.get("linewidth", 1.1),
            alpha=line.get("alpha", 1.0),
            zorder=line.get("zorder", 1),
        )


def _add_text_annotations(*, ax: Any, text_annotations: list[dict[str, Any]] | None) -> None:
    if not text_annotations:
        return
    for annotation in text_annotations:
        if not isinstance(annotation, dict):
            continue
        text = annotation.get("text")
        x = annotation.get("x")
        y = annotation.get("y")
        if text is None or x is None or y is None:
            continue
        ax.text(
            x,
            y,
            str(text),
            color=annotation.get("color", "#222222"),
            fontsize=annotation.get("fontsize", 8),
            ha=annotation.get("ha", "left"),
            va=annotation.get("va", "center"),
            alpha=annotation.get("alpha", 1.0),
            fontweight=annotation.get("fontweight"),
            zorder=annotation.get("zorder", 3),
        )
