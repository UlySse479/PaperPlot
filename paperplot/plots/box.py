"""Box plot implementation."""

from __future__ import annotations

from typing import Any

from paperplot.core.color_advisor import resolve_series_color_map
from paperplot.plots.common import grouped_values, humanize_label
from paperplot.plots.legends import apply_legends, build_extra_legend_handle


def render_box(
    *,
    ax: Any,
    y: list[Any] | None,
    hue: list[Any] | None,
    y_key: str | None,
    hue_key: str | None,
    showfliers: bool | None = None,
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
    **_: Any,
) -> None:
    palette = template.get("defaults", {}).get("box_facecolors", ["#4C78A8", "#72B7B2", "#ECA82C", "#B279A2"])
    if hue is None:
        color_map = resolve_series_color_map(spec or {}, [y_key or "series"])
        facecolor = color_map.get(y_key or "series", palette[0])
        artists = ax.boxplot(
            y or [],
            showfliers=_resolve_showfliers(showfliers, template),
            patch_artist=True,
            widths=0.55,
            medianprops={"color": "#111111", "linewidth": 1.3},
            whiskerprops={"color": "#333333", "linewidth": 1.0},
            capprops={"color": "#333333", "linewidth": 1.0},
            boxprops={"edgecolor": "#333333", "linewidth": 0.9},
        )
        for patch in artists["boxes"]:
            patch.set_facecolor(facecolor)
            patch.set_alpha(0.6)
        ax.set_xticklabels([xlabel or humanize_label(y_key)])
    else:
        grouped = grouped_values(y, hue)
        labels = [str(label) for label in grouped.keys()]
        color_map = resolve_series_color_map(spec or {}, labels)
        artists = ax.boxplot(
            list(grouped.values()),
            tick_labels=labels,
            showfliers=_resolve_showfliers(showfliers, template),
            patch_artist=True,
            widths=0.55,
            medianprops={"color": "#111111", "linewidth": 1.3},
            whiskerprops={"color": "#333333", "linewidth": 1.0},
            capprops={"color": "#333333", "linewidth": 1.0},
            boxprops={"edgecolor": "#333333", "linewidth": 0.9},
        )
        for index, patch in enumerate(artists["boxes"]):
            patch.set_facecolor(color_map.get(labels[index], palette[index % len(palette)]))
            patch.set_alpha(0.6)
        ax.set_xlabel(xlabel or humanize_label(hue_key))
        legend_loc = legend or template.get("defaults", {}).get("legend_loc") or (spec or {}).get("legend", {}).get("loc", "best")
        handles = [
            build_extra_legend_handle(
                {
                    "label": label,
                    "facecolor": color_map.get(label, palette[index % len(palette)]),
                    "edgecolor": "#333333",
                    "alpha": 0.6,
                }
            )
            for index, label in enumerate(labels)
        ]
        apply_legends(
            ax=ax,
            loc=legend_loc,
            title=legend_title,
            bbox_to_anchor=legend_bbox_to_anchor,
            ncol=legend_ncol,
            extra_legends=extra_legends,
            handles=handles,
            labels=labels,
        )
    ax.set_ylabel(ylabel or humanize_label(y_key))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)


def _resolve_showfliers(showfliers: bool | None, template: dict[str, Any]) -> bool:
    if showfliers is not None:
        return showfliers
    return template.get("defaults", {}).get("showfliers", False)
