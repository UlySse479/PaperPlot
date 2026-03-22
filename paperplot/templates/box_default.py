"""Default box template."""

TEMPLATE = {
    "name": "box.default",
    "chart_type": "box",
    "defaults": {"showfliers": False},
    "layout": {"size_token": "single"},
    "mappings": {"required": ["y"], "optional": ["hue"]},
}
