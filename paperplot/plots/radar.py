"""Radar chart implementation."""

from __future__ import annotations

import math
from typing import Any

from paperplot.plots.legends import apply_legends


def render_radar(
    *,
    ax: Any,
    data: Any,
    template: dict[str, Any],
    title: str | None = None,
    legend: str | None = None,
    legend_title: str | None = None,
    legend_bbox_to_anchor: list[float] | tuple[float, float] | None = None,
    legend_ncol: int | None = None,
    extra_legends: list[dict[str, Any]] | None = None,
    spec: dict[str, Any] | None = None,
    **_: Any,
) -> None:
    categories = data.get("categories") if isinstance(data, dict) else None
    series = data.get("series") if isinstance(data, dict) else None
    if not categories or not series:
        raise ValueError("Radar charts require 'categories' and 'series' data.")

    angles = [2 * math.pi * index / len(categories) for index in range(len(categories))]
    angles += angles[:1]
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([angle * 180 / math.pi for angle in angles[:-1]], labels=categories)

    for item in series:
        values = list(item["values"])
        values += values[:1]
        ax.plot(angles, values, label=item["label"], linewidth=2.0)
        ax.fill(angles, values, alpha=0.12)

    ax.set_ylim(template.get("defaults", {}).get("rmin", 0), template.get("defaults", {}).get("rmax", 1))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title, y=1.08)
    legend_loc = legend or template.get("defaults", {}).get("legend_loc") or (spec or {}).get("legend", {}).get("loc", "best")
    apply_legends(
        ax=ax,
        loc=legend_loc,
        title=legend_title,
        bbox_to_anchor=legend_bbox_to_anchor or (1.1, 1.05),
        ncol=legend_ncol,
        extra_legends=extra_legends,
    )
