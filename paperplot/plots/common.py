"""Shared plotting helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def humanize_label(value: str | None) -> str:
    if not value:
        return ""
    return value.replace("_", " ").title()


def group_xy_by_hue(
    x: list[Any] | None,
    y: list[Any] | None,
    hue: list[Any] | None,
) -> dict[Any, dict[str, list[Any]]]:
    grouped: dict[Any, dict[str, list[Any]]] = defaultdict(lambda: {"x": [], "y": []})
    if hue is None:
        return grouped
    for xv, yv, group in zip(x or [], y or [], hue, strict=False):
        grouped[group]["x"].append(xv)
        grouped[group]["y"].append(yv)
    return grouped


def grouped_values(values: list[Any] | None, hue: list[Any] | None) -> dict[Any, list[Any]]:
    grouped: dict[Any, list[Any]] = defaultdict(list)
    if hue is None:
        return grouped
    for value, group in zip(values or [], hue, strict=False):
        grouped[group].append(value)
    return grouped


def rows_from_data(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [dict(row) for row in data]
    if isinstance(data, dict):
        keys = list(data.keys())
        columns = [list(data[key]) for key in keys]
        return [dict(zip(keys, values, strict=False)) for values in zip(*columns, strict=False)]
    if hasattr(data, "to_dict"):
        records = data.to_dict(orient="records")
        return [dict(row) for row in records]
    raise TypeError(f"Unsupported table-like data container: {type(data)!r}")


def resolve_series_arg(data: Any, value: Any) -> Any:
    if isinstance(value, str):
        if isinstance(data, dict) and value in data:
            return list(data[value])
        if hasattr(data, "__getitem__"):
            try:
                extracted = data[value]
            except Exception:
                return value
            if hasattr(extracted, "tolist"):
                return list(extracted.tolist())
            try:
                return list(extracted)
            except TypeError:
                return extracted
    return value
