"""Default scatter template."""

TEMPLATE = {
    "name": "scatter.default",
    "chart_type": "scatter",
    "defaults": {"alpha": 0.85, "size": 36, "legend_loc": "best", "markers": ["o", "s", "^", "D", "P"]},
    "layout": {"size_token": "single"},
    "mappings": {"required": ["x", "y"], "optional": ["hue"]},
}
