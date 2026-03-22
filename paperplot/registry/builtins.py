"""Built-in PaperPlot profiles, styles, templates, and plotters."""

from __future__ import annotations

from paperplot.plots import (
    render_bar,
    render_box,
    render_grouped_bar,
    render_heatmap,
    render_hist,
    render_line,
    render_radar,
    render_scatter,
    render_table,
)
from paperplot.profiles import PROFILES
from paperplot.styles import STYLES
from paperplot.templates import TEMPLATES

PLOTTERS = {
    "line": render_line,
    "bar": render_bar,
    "scatter": render_scatter,
    "grouped_bar": render_grouped_bar,
    "hist": render_hist,
    "box": render_box,
    "heatmap": render_heatmap,
    "radar": render_radar,
    "table": render_table,
}
