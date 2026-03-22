"""Public registry API."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from paperplot.core.serde import load_mapping_file
from paperplot.registry.base import Registry
from paperplot.registry.builtins import PLOTTERS, PROFILES, STYLES, TEMPLATES


profile_registry = Registry("profile")
style_registry = Registry("style")
template_registry = Registry("template")
plotter_registry = Registry("plotter")


for name, payload in PROFILES.items():
    profile_registry.register(name, payload)

for name, payload in STYLES.items():
    style_registry.register(name, payload)

for name, payload in TEMPLATES.items():
    template_registry.register(name, payload)

for name, payload in PLOTTERS.items():
    plotter_registry.register(name, payload)


def register_profile(name: str, spec: Mapping[str, Any]) -> dict[str, Any]:
    return profile_registry.register(name, _with_name(name, spec))


def register_style(name: str, spec: Mapping[str, Any]) -> dict[str, Any]:
    return style_registry.register(name, _with_name(name, spec))


def register_template(name: str, spec: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    payload = dict(spec or {})
    payload.update(kwargs)
    return template_registry.register(name, _with_name(name, payload))


def get_profile(name: str) -> dict[str, Any]:
    return profile_registry.get(name)


def get_style(name: str) -> dict[str, Any]:
    return style_registry.get(name)


def get_template(name: str) -> dict[str, Any]:
    return template_registry.get(name)


def get_plotter(name: str):
    return plotter_registry.get(name)


def list_profiles() -> list[str]:
    return sorted(profile_registry.items().keys())


def list_styles() -> list[str]:
    return sorted(style_registry.items().keys())


def list_templates() -> list[str]:
    return sorted(template_registry.items().keys())


def list_plotters() -> list[str]:
    return sorted(plotter_registry.items().keys())


def load_profiles_from_dir(path: str | Path) -> list[str]:
    loaded: list[str] = []
    for item in _iter_asset_files(path):
        name, data = _read_asset_file(item)
        register_profile(name, data)
        loaded.append(name)
    return loaded


def load_styles_from_dir(path: str | Path) -> list[str]:
    loaded: list[str] = []
    for item in _iter_asset_files(path):
        name, data = _read_asset_file(item)
        register_style(name, data)
        loaded.append(name)
    return loaded


def load_templates_from_dir(path: str | Path) -> list[str]:
    loaded: list[str] = []
    for item in _iter_asset_files(path):
        name, data = _read_asset_file(item)
        register_template(name, data)
        loaded.append(name)
    return loaded


def load_assets_from_dir(path: str | Path) -> dict[str, list[str]]:
    """Load project-local PaperPlot assets from a base directory."""
    base = Path(path)
    loaded = {"profiles": [], "styles": [], "templates": []}

    if (base / "profiles").exists():
        loaded["profiles"] = load_profiles_from_dir(base / "profiles")
    if (base / "styles").exists():
        loaded["styles"] = load_styles_from_dir(base / "styles")
    if (base / "templates").exists():
        loaded["templates"] = load_templates_from_dir(base / "templates")

    return loaded


def autoload_project_assets(root: str | Path = ".") -> dict[str, list[str]]:
    """Autoload assets from common project-local locations."""
    base = Path(root)
    loaded = {"profiles": [], "styles": [], "templates": []}
    for candidate in (base / "paperplot_assets", base / ".paperplot", base):
        if not candidate.exists():
            continue
        current = load_assets_from_dir(candidate)
        for key, values in current.items():
            loaded[key].extend(values)
    return loaded


def _with_name(name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(payload))
    result.setdefault("name", name)
    return result


def _iter_asset_files(path: str | Path) -> list[Path]:
    directory = Path(path)
    if not directory.exists():
        return []

    supported = {".json", ".yaml", ".yml"}
    return [
        item
        for item in sorted(directory.iterdir())
        if item.is_file() and item.suffix.lower() in supported
    ]


def _read_asset_file(path: Path) -> tuple[str, dict[str, Any]]:
    data = load_mapping_file(path)
    name = data.get("name") or path.stem
    return name, data
