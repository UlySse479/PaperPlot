"""Heatmap implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import humanize_label


def render_heatmap(
    *,
    ax: Any,
    data: Any,
    template: dict[str, Any],
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    x_key: str | None = None,
    y_key: str | None = None,
    cmap: str | None = None,
    annotate: bool | None = None,
    **_: Any,
) -> None:
    matrix = data.get("matrix") if isinstance(data, dict) and "matrix" in data else data
    if not isinstance(matrix, list):
        raise TypeError("Heatmap data must be a 2D list or a mapping with a 'matrix' key.")

    x_labels = data.get("x_labels") if isinstance(data, dict) else None
    y_labels = data.get("y_labels") if isinstance(data, dict) else None
    final_cmap = cmap or template.get("defaults", {}).get("cmap", "viridis")
    final_annotate = annotate if annotate is not None else template.get("defaults", {}).get("annotate", False)

    image = ax.imshow(matrix, aspect="auto", cmap=final_cmap)
    ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    if x_labels:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels([str(label) for label in x_labels], rotation=30, ha="right")
    if y_labels:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels([str(label) for label in y_labels])

    if final_annotate:
        flat_values = [value for row in matrix for value in row]
        value_min = min(flat_values)
        value_max = max(flat_values)
        midpoint = (value_min + value_max) / 2
        for row_index, row in enumerate(matrix):
            for col_index, value in enumerate(row):
                color = "white" if value >= midpoint else "#111111"
                ax.text(
                    col_index,
                    row_index,
                    f"{value:.2f}" if isinstance(value, float) else str(value),
                    ha="center",
                    va="center",
                    fontsize=7,
                    color=color,
                )

    ax.set_xlabel(xlabel or humanize_label(x_key))
    ax.set_ylabel(ylabel or humanize_label(y_key))
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title)
