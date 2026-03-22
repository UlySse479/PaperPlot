"""Default grouped bar template."""

TEMPLATE = {
    "name": "grouped_bar.default",
    "chart_type": "grouped_bar",
    "defaults": {"legend_loc": "best", "bar_width": 0.22},
    "layout": {"size_token": "single"},
    "mappings": {"required": ["x", "y", "hue"], "optional": []},
}
