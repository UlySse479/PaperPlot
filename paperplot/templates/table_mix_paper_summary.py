"""Paper-summary mixed layout template."""

TEMPLATE = {
    "name": "table_mix.paper_summary",
    "base": "table_mix.default",
    "defaults": {
        "title": "Paper Summary",
        "panel_labels": "auto",
    },
    "layout": {"size_token": "double", "nrows": 1, "ncols": 2, "width_ratios": [1.0, 1.8]},
}
