"""Axis formatting helpers."""

from __future__ import annotations

from typing import Any


def apply_axis_formatters(
    *,
    ax: Any,
    xformatter: str | None = None,
    yformatter: str | None = None,
    xscale: str | None = None,
    yscale: str | None = None,
) -> None:
    if xscale:
        ax.set_xscale(xscale)
    if yscale:
        ax.set_yscale(yscale)
    if xformatter:
        _apply_single_formatter(ax.xaxis, xformatter)
    if yformatter:
        _apply_single_formatter(ax.yaxis, yformatter)


def _apply_single_formatter(axis: Any, formatter_name: str) -> None:
    import matplotlib.ticker as mticker

    if formatter_name == "percent":
        axis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
        return
    if formatter_name == "percent100":
        axis.set_major_formatter(mticker.PercentFormatter(xmax=100.0))
        return
    if formatter_name == "scientific":
        axis.set_major_formatter(mticker.FormatStrFormatter("%.1e"))
        return
    if formatter_name == "compact":
        axis.set_major_formatter(mticker.FuncFormatter(_compact_number))
        return
    raise ValueError(f"Unknown axis formatter: {formatter_name}")


def _compact_number(value: float, _: int) -> str:
    thresholds = [(1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")]
    for threshold, suffix in thresholds:
        if abs(value) >= threshold:
            return f"{value / threshold:.1f}{suffix}"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"
