"""Default histogram template."""

TEMPLATE = {
    "name": "hist.default",
    "chart_type": "hist",
    "defaults": {"bins": 20, "density": False, "title": "Distribution"},
    "layout": {"size_token": "single"},
    "mappings": {"required": ["x"], "optional": []},
}
