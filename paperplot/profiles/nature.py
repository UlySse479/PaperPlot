"""Nature publication profile."""

PROFILE = {
    "name": "nature",
    "font": {
        "family": "sans-serif",
        "size": 8,
        "title_size": 8,
        "label_size": 8,
        "tick_size": 7,
        "mathtext_fontset": "dejavusans",
    },
    "sizes": {
        "single": [3.5, 2.4],
        "double": [7.2, 3.2],
        "square": [3.2, 3.2],
    },
    "export": {
        "formats": ["pdf", "png"],
        "dpi": 300,
        "bbox_inches": "tight",
        "transparent": False,
    },
}
