"""Grouped bar chart implementation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from paperplot.core.color_advisor import resolve_series_color_map
from paperplot.plots.annotations import add_significance_annotations, compile_significance_annotations
from paperplot.plots.common import humanize_label, resolve_series_arg
from paperplot.plots.legends import apply_legends


def render_grouped_bar(
    *,
    ax: Any,
    x: list[Any] | None,
    y: list[Any] | None,
    hue: list[Any] | None,
    x_key: str | None,
    y_key: str | None,
    template: dict[str, Any],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    legend: str | None = None,
    legend_title: str | None = None,
    legend_bbox_to_anchor: list[float] | tuple[float, float] | None = None,
    legend_ncol: int | None = None,
    extra_legends: list[dict[str, Any]] | None = None,
    spec: dict[str, Any] | None = None,
    data: Any = None,
    yerr: Any = None,
    orientation: str | None = None,
    xlim: list[float] | tuple[float, float] | None = None,
    ylim: list[float] | tuple[float, float] | None = None,
    xticks: list[Any] | None = None,
    yticks: list[Any] | None = None,
    show_value_labels: bool | None = None,
    value_label_format: str | None = None,
    reference_lines: list[dict[str, Any]] | None = None,
    annotations: list[dict[str, Any]] | None = None,
    significance: list[dict[str, Any]] | None = None,
    **_: Any,
) -> None:
    if hue is None:
        raise ValueError("Grouped bar plots require 'hue' mappings.")

    grouped: dict[Any, dict[Any, Any]] = defaultdict(dict)
    categories: list[Any] = []
    series_order: list[Any] = []

    for xv, yv, hv in zip(x or [], y or [], hue, strict=False):
        if xv not in categories:
            categories.append(xv)
        if hv not in series_order:
            series_order.append(hv)
        grouped[hv][xv] = yv

    width = template.get("defaults", {}).get("bar_width", 0.8 / max(len(series_order), 1))
    final_orientation = orientation or template.get("defaults", {}).get("orientation", "vertical")
    is_horizontal = final_orientation == "horizontal"
    centers = list(range(len(categories)))
    start = -width * (len(series_order) - 1) / 2
    yerr_values = resolve_series_arg(data, yerr)
    x_lookup: dict[Any, float] = {}
    color_map = resolve_series_color_map(spec or {}, list(series_order))

    for index, label in enumerate(series_order):
        offset = start + index * width
        values = [grouped[label].get(category, 0) for category in categories]
        errs = None
        if yerr_values is not None:
            errs = [err for err, hue_value in zip(yerr_values, hue, strict=False) if hue_value == label]
        positions = [center + offset for center in centers]
        for category, position in zip(categories, positions, strict=False):
            x_lookup[(category, label)] = position
        if is_horizontal:
            bars = ax.barh(
                positions,
                values,
                height=width,
                label=str(label),
                xerr=errs,
                color=color_map.get(label),
                capsize=3 if errs is not None else 0,
                edgecolor="none",
                linewidth=0.0,
                zorder=3,
                alpha=0.95,
            )
        else:
            bars = ax.bar(
                positions,
                values,
                width=width,
                label=str(label),
                yerr=errs,
                color=color_map.get(label),
                capsize=3 if errs is not None else 0,
                edgecolor="#222222",
                linewidth=0.8,
                zorder=3,
                alpha=0.92,
            )
        if show_value_labels:
            _add_value_labels(
                ax=ax,
                bars=bars,
                is_horizontal=is_horizontal,
                value_label_format=value_label_format or "{:.1f}",
            )

    if is_horizontal:
        ax.set_yticks(centers)
        ax.set_yticklabels([str(category) for category in categories])
        ax.set_xlabel(humanize_label(y_key) if xlabel is None else xlabel)
        ax.set_ylabel(humanize_label(x_key) if ylabel is None else ylabel)
    else:
        ax.set_xticks(centers)
        ax.set_xticklabels([str(category) for category in categories], rotation=20)
        ax.set_xlabel(humanize_label(x_key) if xlabel is None else xlabel)
        ax.set_ylabel(humanize_label(y_key) if ylabel is None else ylabel)
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)
    legend_loc = legend or template.get("defaults", {}).get("legend_loc") or (spec or {}).get("legend", {}).get("loc", "best")
    apply_legends(
        ax=ax,
        loc=legend_loc,
        title=legend_title,
        ncol=legend_ncol,
        bbox_to_anchor=legend_bbox_to_anchor,
        extra_legends=extra_legends,
    )
    _apply_axis_overrides(ax=ax, is_horizontal=is_horizontal, xlim=xlim, ylim=ylim, xticks=xticks, yticks=yticks)
    _add_reference_lines(ax=ax, reference_lines=reference_lines, is_horizontal=is_horizontal)
    ax.margins(x=0.04 if not is_horizontal else 0.02, y=0.06 if is_horizontal else 0.04)
    final_annotations = list(annotations or [])
    final_annotations.extend(compile_significance_annotations(significance, within_groups=categories))
    add_significance_annotations(ax=ax, annotations=final_annotations, x_lookup=x_lookup)


def _apply_axis_overrides(
    *,
    ax: Any,
    is_horizontal: bool,
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
    if is_horizontal:
        ax.invert_yaxis()


def _add_reference_lines(*, ax: Any, reference_lines: list[dict[str, Any]] | None, is_horizontal: bool) -> None:
    if not reference_lines:
        return
    for line in reference_lines:
        if not isinstance(line, dict):
            continue
        value = line.get("x" if is_horizontal else "y")
        if value is None:
            continue
        if is_horizontal:
            ax.axvline(
                x=value,
                color=line.get("color", "#888888"),
                linestyle=line.get("linestyle", ":"),
                linewidth=line.get("linewidth", 1.0),
                alpha=line.get("alpha", 1.0),
                zorder=line.get("zorder", 1),
            )
        else:
            ax.axhline(
                y=value,
                color=line.get("color", "#888888"),
                linestyle=line.get("linestyle", ":"),
                linewidth=line.get("linewidth", 1.0),
                alpha=line.get("alpha", 1.0),
                zorder=line.get("zorder", 1),
            )


def _add_value_labels(*, ax: Any, bars: Any, is_horizontal: bool, value_label_format: str) -> None:
    for bar in bars:
        if is_horizontal:
            value = bar.get_width()
            x = value + 0.8
            y = bar.get_y() + bar.get_height() / 2
            ax.text(x, y, value_label_format.format(value), va="center", ha="left", fontsize=8)
        else:
            value = bar.get_height()
            x = bar.get_x() + bar.get_width() / 2
            y = value
            ax.text(x, y + 0.5, value_label_format.format(value), va="bottom", ha="center", fontsize=8)
