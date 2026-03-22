"""Generic registry implementation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class Registry:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._items: dict[str, Any] = {}

    def register(self, name: str, value: Any) -> Any:
        self._items[name] = deepcopy(value)
        return self._items[name]

    def get(self, name: str) -> Any:
        try:
            return deepcopy(self._items[name])
        except KeyError as exc:
            raise KeyError(f"Unknown {self.kind}: {name}") from exc

    def items(self) -> dict[str, Any]:
        return deepcopy(self._items)
