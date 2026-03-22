"""Built-in plot implementations."""

from paperplot.plots.bar import render_bar
from paperplot.plots.box import render_box
from paperplot.plots.grouped_bar import render_grouped_bar
from paperplot.plots.heatmap import render_heatmap
from paperplot.plots.hist import render_hist
from paperplot.plots.line import render_line
from paperplot.plots.radar import render_radar
from paperplot.plots.scatter import render_scatter
from paperplot.plots.table import render_table

__all__ = [
    "render_bar",
    "render_box",
    "render_grouped_bar",
    "render_heatmap",
    "render_hist",
    "render_line",
    "render_radar",
    "render_scatter",
    "render_table",
]
