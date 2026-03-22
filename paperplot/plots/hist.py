"""Histogram implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import humanize_label


def render_hist(
    *,
    ax: Any,
    x: list[Any] | None,
    x_key: str | None,
    bins: int | None = None,
    density: bool | None = None,
    template: dict[str, Any],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    **_: Any,
) -> None:
    final_density = density if density is not None else template.get("defaults", {}).get("density", False)
    ax.hist(
        x or [],
        bins=bins or template.get("defaults", {}).get("bins", 20),
        density=final_density,
        edgecolor="#222222",
        linewidth=0.75,
        alpha=0.9,
    )
    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or ("Density" if final_density else "Count"))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)
