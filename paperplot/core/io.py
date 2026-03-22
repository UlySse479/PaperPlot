"""Input normalization helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping


def load_data(data: Any) -> Any:
    """Load CSV files and pass through in-memory objects unchanged."""
    if isinstance(data, (str, Path)):
        path = Path(data)
        if path.suffix.lower() == ".csv":
            return _load_csv(path)
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return data


def extract_series(data: Any, key: str | None) -> list[Any] | None:
    """Extract a column from common data containers."""
    if key is None:
        return None

    if hasattr(data, "__getitem__") and not isinstance(data, list):
        values = data[key]
        if hasattr(values, "tolist"):
            return list(values.tolist())
        return list(values)

    if isinstance(data, list):
        return [row[key] for row in data]

    raise TypeError(f"Unsupported data container for key lookup: {type(data)!r}")


def _load_csv(path: Path) -> dict[str, list[Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns: dict[str, list[Any]] = {name: [] for name in reader.fieldnames or []}
        for row in reader:
            for key, value in row.items():
                columns[key].append(_coerce_scalar(value))
    return columns


def _coerce_scalar(value: str | None) -> Any:
    if value is None:
        return None

    for caster in (int, float):
        try:
            return caster(value)
        except (TypeError, ValueError):
            continue
    return value
