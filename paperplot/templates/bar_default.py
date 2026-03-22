"""Default bar template."""

TEMPLATE = {
    "name": "bar.default",
    "chart_type": "bar",
    "defaults": {"sort": False},
    "layout": {"size_token": "single"},
    "mappings": {"required": ["x", "y"], "optional": []},
}
