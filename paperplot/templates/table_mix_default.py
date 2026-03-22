"""Default table-and-figure mixed layout template."""

TEMPLATE = {
    "name": "table_mix.default",
    "chart_type": "table_mix",
    "defaults": {"title": "Mixed Layout", "panel_labels": "auto"},
    "layout": {"size_token": "double", "nrows": 1, "ncols": 2, "width_ratios": [1.2, 1.8]},
    "mappings": {"required": [], "optional": []},
}
