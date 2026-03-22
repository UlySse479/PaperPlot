"""Default PaperPlot style."""

STYLE = {
    "name": "default",
    "palette": {"colors": ["#4C78A8", "#F58518", "#54A24B", "#E45756"]},
    "axes": {
        "grid": False,
        "grid_alpha": 0.2,
        "grid_linewidth": 0.6,
        "linewidth": 0.9,
        "edgecolor": "#222222",
        "tick_direction": "out",
        "tick_size": 3.5,
        "tick_width": 0.8,
        "spines_top": False,
        "spines_right": False,
    },
    "legend": {"frameon": False, "loc": "best", "fontsize": 8, "handlelength": 1.8},
    "lines": {"linewidth": 2.0, "markersize": 5, "markeredgewidth": 0.8},
}
