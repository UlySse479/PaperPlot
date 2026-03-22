"""Figure export helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def save_figure(fig: Any, path: str | Path, export_config: dict[str, Any]) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    dpi = export_config.get("dpi", 300)
    bbox_inches = export_config.get("bbox_inches", "tight")
    transparent = export_config.get("transparent", False)

    fig.savefig(
        destination,
        dpi=dpi,
        bbox_inches=bbox_inches,
        transparent=transparent,
    )
    return destination
