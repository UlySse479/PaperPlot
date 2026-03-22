"""Table implementation."""

from __future__ import annotations

from typing import Any

from paperplot.plots.common import rows_from_data


def render_table(
    *,
    ax: Any,
    data: Any,
    template: dict[str, Any],
    title: str | None = None,
    columns: list[str] | None = None,
    **_: Any,
) -> None:
    rows = rows_from_data(data)
    if not rows:
        raise ValueError("Table data must contain at least one row.")

    column_names = columns or list(rows[0].keys())
    cell_text = [[row.get(column, "") for column in column_names] for row in rows]

    ax.axis("off")
    table = ax.table(cellText=cell_text, colLabels=column_names, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(template.get("defaults", {}).get("fontsize", 8))
    table.scale(1.0, template.get("defaults", {}).get("yscale", 1.35))
    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#EAEAEA")
    final_title = title or template.get("defaults", {}).get("title")
    if final_title:
        ax.set_title(final_title, pad=10)
