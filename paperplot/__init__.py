"""Public API for PaperPlot."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from paperplot.registry.api import (
    autoload_project_assets,
    get_profile,
    get_style,
    get_template,
    list_plotters,
    list_profiles,
    list_styles,
    list_templates,
    load_assets_from_dir,
    load_profiles_from_dir,
    load_styles_from_dir,
    load_templates_from_dir,
    register_profile,
    register_style,
    register_template,
)

__all__ = [
    "autoload_project_assets",
    "get_profile",
    "get_style",
    "get_template",
    "list_plotters",
    "list_profiles",
    "list_styles",
    "list_templates",
    "load_assets_from_dir",
    "load_profiles_from_dir",
    "load_styles_from_dir",
    "load_templates_from_dir",
    "managed_figure",
    "plot",
    "plot_from_config",
    "render_gallery",
    "register_profile",
    "register_style",
    "register_template",
    "render_template",
    "use_style",
]


def plot(*args: Any, **kwargs: Any):
    from paperplot.core.renderer import plot as _plot

    return _plot(*args, **kwargs)


def render_template(*args: Any, **kwargs: Any):
    from paperplot.core.renderer import render_template as _render_template

    return _render_template(*args, **kwargs)


def plot_from_config(*args: Any, **kwargs: Any):
    from paperplot.core.renderer import plot_from_config as _plot_from_config

    return _plot_from_config(*args, **kwargs)


def render_gallery(*args: Any, **kwargs: Any):
    from paperplot.gallery import render_gallery as _render_gallery

    return _render_gallery(*args, **kwargs)


def use_style(*args: Any, **kwargs: Any):
    from paperplot.core.style import use_style as _use_style

    return _use_style(*args, **kwargs)


@contextmanager
def managed_figure(rendered: Any):
    """Yield a PaperPlot render result and close its Matplotlib figure on exit."""
    fig = None
    try:
        if isinstance(rendered, tuple) and rendered:
            fig = rendered[0]
        yield rendered
    finally:
        if fig is not None:
            import matplotlib.pyplot as plt

            plt.close(fig)
