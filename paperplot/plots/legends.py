"""Shared legend helpers for PaperPlot plotters."""

from __future__ import annotations

from typing import Any


def apply_legends(
    *,
    ax: Any,
    loc: str,
    title: str | None = None,
    bbox_to_anchor: list[float] | tuple[float, float] | None = None,
    ncol: int | None = None,
    extra_legends: list[dict[str, Any]] | None = None,
    handles: list[Any] | None = None,
    labels: list[str] | None = None,
) -> Any:
    if handles is None and labels is None:
        primary_legend = ax.legend(
            loc=loc,
            title=title,
            ncol=ncol or 1,
            bbox_to_anchor=tuple(bbox_to_anchor) if bbox_to_anchor is not None else None,
        )
    else:
        primary_legend = ax.legend(
            handles,
            labels,
            loc=loc,
            title=title,
            ncol=ncol or 1,
            bbox_to_anchor=tuple(bbox_to_anchor) if bbox_to_anchor is not None else None,
        )

    _add_extra_legends(ax=ax, extra_legends=extra_legends, primary_legend=primary_legend)
    return primary_legend


def build_extra_legend_handle(entry: dict[str, Any]) -> Any:
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    facecolor = entry.get("facecolor")
    edgecolor = entry.get("edgecolor")
    marker = entry.get("marker")
    linestyle = entry.get("linestyle", "-")
    linewidth = entry.get("linewidth", 1.2)

    if facecolor is not None or edgecolor is not None:
        return Patch(
            facecolor=facecolor if facecolor is not None else "none",
            edgecolor=edgecolor if edgecolor is not None else "#666666",
            linewidth=linewidth,
            alpha=entry.get("alpha", 1.0),
        )

    return Line2D(
        [0],
        [0],
        color=entry.get("color", "#666666"),
        linestyle=linestyle,
        linewidth=linewidth,
        marker=marker,
        markersize=entry.get("markersize", 4.0),
        markerfacecolor=entry.get("markerfacecolor"),
        markeredgecolor=entry.get("markeredgecolor"),
        alpha=entry.get("alpha", 1.0),
    )


def _add_extra_legends(*, ax: Any, extra_legends: list[dict[str, Any]] | None, primary_legend: Any) -> None:
    if not extra_legends:
        return
    if primary_legend is not None:
        ax.add_artist(primary_legend)

    for legend in extra_legends:
        if not isinstance(legend, dict):
            continue
        entries = legend.get("entries")
        if not isinstance(entries, list) or not entries:
            continue

        handles = []
        labels = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            handles.append(build_extra_legend_handle(entry))
            labels.append(str(entry.get("label", "")))

        if not handles:
            continue

        ax.legend(
            handles,
            labels,
            loc=legend.get("loc", "best"),
            title=legend.get("title"),
            frameon=legend.get("frameon", False),
            fontsize=legend.get("fontsize"),
            title_fontsize=legend.get("title_fontsize"),
            handlelength=legend.get("handlelength"),
            ncol=legend.get("ncol", 1),
            bbox_to_anchor=tuple(legend["bbox_to_anchor"]) if legend.get("bbox_to_anchor") is not None else None,
        )
