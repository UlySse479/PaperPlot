"""Box plot implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import grouped_values, humanize_label


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
    **_: Any,
) -> None:
    palette = template.get("defaults", {}).get("box_facecolors", ["#4C78A8", "#72B7B2", "#ECA82C", "#B279A2"])
    if hue is None:
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
            patch.set_facecolor(palette[0])
            patch.set_alpha(0.6)
        ax.set_xticklabels([xlabel or humanize_label(y_key)])
    else:
        grouped = grouped_values(y, hue)
        artists = ax.boxplot(
            list(grouped.values()),
            tick_labels=[str(label) for label in grouped.keys()],
            showfliers=_resolve_showfliers(showfliers, template),
            patch_artist=True,
            widths=0.55,
            medianprops={"color": "#111111", "linewidth": 1.3},
            whiskerprops={"color": "#333333", "linewidth": 1.0},
            capprops={"color": "#333333", "linewidth": 1.0},
            boxprops={"edgecolor": "#333333", "linewidth": 0.9},
        )
        for index, patch in enumerate(artists["boxes"]):
            patch.set_facecolor(palette[index % len(palette)])
            patch.set_alpha(0.6)
        ax.set_xlabel(xlabel or humanize_label(hue_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)


def _resolve_showfliers(showfliers: bool | None, template: dict[str, Any]) -> bool:
    if showfliers is not None:
        return showfliers
    return template.get("defaults", {}).get("showfliers", False)
