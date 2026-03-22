"""Bar plot implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.annotations import add_significance_annotations, compile_significance_annotations
from paperplot.plots.common import humanize_label, resolve_series_arg


def render_bar(
    *,
    ax: Any,
    x: list[Any] | None,
    y: list[Any] | None,
    x_key: str | None,
    y_key: str | None,
    sort: bool | None = None,
    template: dict[str, Any],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    yerr: Any = None,
    data: Any = None,
    annotations: list[dict[str, Any]] | None = None,
    significance: list[dict[str, Any]] | None = None,
    **_: Any,
) -> None:
    items = list(zip(x or [], y or [], strict=False))
    should_sort = sort or template.get("defaults", {}).get("sort", False)
    if should_sort:
        items = sorted(items, key=lambda item: item[1], reverse=True)

    xs = [item[0] for item in items]
    ys = [item[1] for item in items]
    yerr_values = resolve_series_arg(data, yerr)
    if yerr_values is not None and should_sort:
        yerr_lookup = {xv: err for xv, err in zip(x or [], yerr_values, strict=False)}
        yerr_values = [yerr_lookup[item[0]] for item in items]
    bars = ax.bar(xs, ys, yerr=yerr_values, capsize=3 if yerr_values is not None else 0, edgecolor="#222222", linewidth=0.8, zorder=3)
    for bar in bars:
        bar.set_alpha(0.9)
    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)
    ax.tick_params(axis="x", rotation=20)
    ax.margins(x=0.04)
    final_annotations = list(annotations or [])
    final_annotations.extend(compile_significance_annotations(significance, within_groups=xs))
    add_significance_annotations(
        ax=ax,
        annotations=final_annotations,
        x_lookup={value: index for index, value in enumerate(xs)},
    )
