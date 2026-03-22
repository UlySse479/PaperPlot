"""Default line template."""

TEMPLATE = {
    "name": "line.default",
    "chart_type": "line",
    "defaults": {
        "legend_loc": "best",
        "marker": True,
        "markers": ["o", "s", "^", "D", "P"],
        "linestyles": ["-", "--", "-.", ":"],
    },
    "layout": {"size_token": "single"},
    "mappings": {"required": ["x", "y"], "optional": ["hue"]},
}
