"""Line plot implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import group_xy_by_hue, humanize_label, resolve_series_arg


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
    legend: str | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    yerr: Any = None,
    y_lower: Any = None,
    y_upper: Any = None,
    **_: Any,
) -> None:
    marker_enabled = template.get("defaults", {}).get("marker", True) if marker is None else marker
    legend_loc = legend or template.get("defaults", {}).get("legend_loc") or spec.get("legend", {}).get("loc", "best")
    markers = template.get("defaults", {}).get("markers", ["o", "s", "^", "D", "P"])
    linestyles = template.get("defaults", {}).get("linestyles", ["-", "--", "-.", ":"])
    yerr_values = resolve_series_arg(data, yerr)
    y_lower_values = resolve_series_arg(data, y_lower)
    y_upper_values = resolve_series_arg(data, y_upper)

    if hue is None:
        _plot_line_series(
            ax=ax,
            x_values=x or [],
            y_values=y or [],
            marker_style=markers[0] if marker_enabled else None,
            linestyle=linestyles[0],
            label=y_key,
            yerr_values=yerr_values,
            y_lower_values=y_lower_values,
            y_upper_values=y_upper_values,
        )
    else:
        grouped = group_xy_by_hue(x, y, hue)
        for index, (group, series) in enumerate(grouped.items()):
            ordered = sorted(zip(series["x"], series["y"], strict=False), key=lambda item: item[0])
            _plot_line_series(
                ax=ax,
                x_values=[item[0] for item in ordered],
                y_values=[item[1] for item in ordered],
                marker_style=markers[index % len(markers)] if marker_enabled else None,
                linestyle=linestyles[index % len(linestyles)],
                label=str(group),
                yerr_values=_subset_series(yerr_values, hue, group),
                y_lower_values=_subset_series(y_lower_values, hue, group),
                y_upper_values=_subset_series(y_upper_values, hue, group),
            )
        ax.legend(loc=legend_loc)

    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    ax.margins(x=0.02, y=0.08)
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
            clip_on=False,
        )
    if y_lower_values is not None and y_upper_values is not None:
        ax.fill_between(x_values, y_lower_values, y_upper_values, alpha=0.18)


def _subset_series(series: Any, hue: list[Any] | None, group: Any) -> Any:
    if series is None or hue is None:
        return series
    return [value for value, group_value in zip(series, hue, strict=False) if group_value == group]
