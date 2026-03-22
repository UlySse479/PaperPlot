"""Scatter plot implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import group_xy_by_hue, humanize_label, resolve_series_arg


def render_scatter(
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
    alpha: float | None = None,
    size: float | None = None,
    spec: dict[str, Any] | None = None,
    data: Any = None,
    xerr: Any = None,
    yerr: Any = None,
    labels: Any = None,
    annotate_points: bool | None = None,
    pareto_frontier: bool | None = None,
    frontier_direction: str | None = None,
    **_: Any,
) -> None:
    final_alpha = alpha if alpha is not None else template.get("defaults", {}).get("alpha", 0.85)
    final_size = size if size is not None else template.get("defaults", {}).get("size", 36)
    legend_loc = legend or template.get("defaults", {}).get("legend_loc") or (spec or {}).get("legend", {}).get("loc", "best")
    final_annotate_points = annotate_points if annotate_points is not None else template.get("defaults", {}).get("annotate_points", False)
    final_pareto_frontier = pareto_frontier if pareto_frontier is not None else template.get("defaults", {}).get("pareto_frontier", False)
    final_frontier_direction = frontier_direction or template.get("defaults", {}).get("frontier_direction", "max_y_min_x")
    xerr_values = resolve_series_arg(data, xerr)
    yerr_values = resolve_series_arg(data, yerr)
    label_values = resolve_series_arg(data, labels)

    all_points: list[tuple[Any, Any, Any]] = []

    if hue is None:
        ax.scatter(x or [], y or [], alpha=final_alpha, s=final_size, edgecolors="#222222", linewidths=0.5)
        if xerr_values is not None or yerr_values is not None:
            ax.errorbar(x or [], y or [], xerr=xerr_values, yerr=yerr_values, fmt="none", ecolor="#444444", alpha=0.65, capsize=3)
        all_points.extend(zip(x or [], y or [], label_values or [None] * len(x or []), strict=False))
    else:
        grouped = group_xy_by_hue(x, y, hue)
        markers = template.get("defaults", {}).get("markers", ["o", "s", "^", "D", "P"])
        for index, (group, series) in enumerate(grouped.items()):
            group_indices = [i for i, group_value in enumerate(hue or []) if group_value == group]
            ax.scatter(
                series["x"],
                series["y"],
                alpha=final_alpha,
                s=final_size,
                marker=markers[index % len(markers)],
                label=str(group),
                edgecolors="#222222",
                linewidths=0.5,
            )
            if xerr_values is not None or yerr_values is not None:
                group_xerr = [xerr_values[i] for i in group_indices] if xerr_values is not None else None
                group_yerr = [yerr_values[i] for i in group_indices] if yerr_values is not None else None
                ax.errorbar(series["x"], series["y"], xerr=group_xerr, yerr=group_yerr, fmt="none", ecolor="#444444", alpha=0.65, capsize=3)
            group_labels = [label_values[i] for i in group_indices] if label_values is not None else [None] * len(series["x"])
            all_points.extend(zip(series["x"], series["y"], group_labels, strict=False))
        ax.legend(loc=legend_loc)

    if final_annotate_points and label_values is not None:
        for xv, yv, label in all_points:
            if label is None:
                continue
            ax.annotate(
                str(label),
                (xv, yv),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=7,
                color="#222222",
            )

    if final_pareto_frontier:
        frontier = _compute_frontier(all_points, final_frontier_direction)
        if frontier:
            ax.plot(
                [point[0] for point in frontier],
                [point[1] for point in frontier],
                linestyle="--",
                linewidth=1.0,
                color="#444444",
                alpha=0.8,
                zorder=2,
            )

    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)
    ax.margins(x=0.05, y=0.08)


def _compute_frontier(points: list[tuple[Any, Any, Any]], direction: str) -> list[tuple[Any, Any, Any]]:
    numeric_points = [point for point in points if isinstance(point[0], (int, float)) and isinstance(point[1], (int, float))]
    if not numeric_points:
        return []

    if direction == "max_y_min_x":
        ordered = sorted(numeric_points, key=lambda point: point[0])
        frontier: list[tuple[Any, Any, Any]] = []
        best_y: float | None = None
        for point in ordered:
            if best_y is None or point[1] >= best_y:
                frontier.append(point)
                best_y = float(point[1])
        return frontier

    if direction == "max_y_max_x":
        ordered = sorted(numeric_points, key=lambda point: point[0], reverse=True)
        frontier: list[tuple[Any, Any, Any]] = []
        best_y: float | None = None
        for point in ordered:
            if best_y is None or point[1] >= best_y:
                frontier.append(point)
                best_y = float(point[1])
        return list(reversed(frontier))

    raise ValueError(f"Unknown frontier direction: {direction}")
