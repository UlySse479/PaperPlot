"""Pareto frontier scatter template."""

TEMPLATE = {
    "name": "scatter.pareto_frontier",
    "base": "scatter.default",
    "defaults": {
        "annotate_points": True,
        "pareto_frontier": True,
        "frontier_direction": "max_y_min_x",
        "title": "Pareto Frontier",
        "size": 48,
    },
}
