"""Merging helpers for PaperPlot configuration resolution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def deep_merge(base: Mapping[str, Any], extra: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge two mappings into a new dictionary."""
    result = deepcopy(dict(base))
    for key, value in extra.items():
        if (
            key in result
            and isinstance(result[key], Mapping)
            and isinstance(value, Mapping)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def apply_dotted_overrides(
    config: Mapping[str, Any], overrides: Mapping[str, Any] | None
) -> dict[str, Any]:
    """Apply dotted-path overrides like ``axes.grid`` to nested dictionaries."""
    result = deepcopy(dict(config))
    if not overrides:
        return result

    for path, value in overrides.items():
        target: dict[str, Any] = result
        parts = path.split(".")
        for part in parts[:-1]:
            current = target.get(part)
            if not isinstance(current, dict):
                current = {}
                target[part] = current
            target = current
        target[parts[-1]] = value
    return result
