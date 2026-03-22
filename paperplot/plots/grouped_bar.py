"""Grouped bar chart implementation."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from paperplot.plots.annotations import add_significance_annotations, compile_significance_annotations
from paperplot.plots.common import humanize_label, resolve_series_arg


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
    spec: dict[str, Any] | None = None,
    data: Any = None,
    yerr: Any = None,
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
    centers = list(range(len(categories)))
    start = -width * (len(series_order) - 1) / 2
    yerr_values = resolve_series_arg(data, yerr)
    x_lookup: dict[Any, float] = {}

    for index, label in enumerate(series_order):
        offset = start + index * width
        values = [grouped[label].get(category, 0) for category in categories]
        errs = None
        if yerr_values is not None:
            errs = [err for err, hue_value in zip(yerr_values, hue, strict=False) if hue_value == label]
        positions = [center + offset for center in centers]
        for category, position in zip(categories, positions, strict=False):
            x_lookup[(category, label)] = position
        ax.bar(
            positions,
            values,
            width=width,
            label=str(label),
            yerr=errs,
            capsize=3 if errs is not None else 0,
            edgecolor="#222222",
            linewidth=0.8,
            zorder=3,
            alpha=0.92,
        )

    ax.set_xticks(centers)
    ax.set_xticklabels([str(category) for category in categories], rotation=20)
    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)
    legend_loc = legend or template.get("defaults", {}).get("legend_loc") or (spec or {}).get("legend", {}).get("loc", "best")
    ax.legend(loc=legend_loc)
    ax.margins(x=0.04)
    final_annotations = list(annotations or [])
    final_annotations.extend(compile_significance_annotations(significance, within_groups=categories))
    add_significance_annotations(ax=ax, annotations=final_annotations, x_lookup=x_lookup)
