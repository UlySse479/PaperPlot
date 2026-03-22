"""Configuration resolution for profiles, styles, and templates."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from paperplot.core.merge import apply_dotted_overrides, deep_merge
from paperplot.core.serde import load_mapping_file
from paperplot.registry.api import get_profile, get_style, get_template


DEFAULT_PROFILE = "icml"
DEFAULT_STYLE = "academic-muted"


def resolve_profile(name: str | None) -> dict[str, Any]:
    return deepcopy(get_profile(name or DEFAULT_PROFILE))


def resolve_style(name: str | None) -> dict[str, Any]:
    style = deepcopy(get_style(name or DEFAULT_STYLE))
    base_name = style.pop("base", None)
    if not base_name:
        return style
    return deep_merge(resolve_style(base_name), style)


def resolve_template(name: str) -> dict[str, Any]:
    template = deepcopy(get_template(name))
    base_name = template.pop("base", None)
    if not base_name:
        return template
    return deep_merge(resolve_template(base_name), template)


def resolve_figure_spec(
    *,
    template: str,
    profile: str | None = None,
    visual: str | None = None,
    size: str | None = None,
    override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    profile_spec = resolve_profile(profile)
    style_spec = resolve_style(visual)
    template_spec = resolve_template(template)

    spec = deep_merge(profile_spec, style_spec)
    spec = deep_merge(spec, {"template": template_spec})

    size_token = size or template_spec.get("layout", {}).get("size_token", "single")
    figsize = profile_spec.get("sizes", {}).get(size_token)
    if figsize is None:
        raise KeyError(f"Unknown size token {size_token!r} for profile {profile_spec['name']!r}")

    spec["figure"] = {
        "size_token": size_token,
        "figsize": tuple(figsize),
    }
    return apply_dotted_overrides(spec, override)


def load_yaml_config(path: str) -> dict[str, Any]:
    return load_mapping_file(path)


def load_plot_config(config: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    """Load a plot configuration from a mapping or supported file path."""
    if isinstance(config, Mapping):
        return deepcopy(dict(config))
    return load_mapping_file(config)
