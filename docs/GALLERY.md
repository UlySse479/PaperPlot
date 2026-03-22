# PaperPlot Gallery

This gallery is intentionally small and representative. Each figure is chosen to exercise a distinct publication-oriented rendering pattern and to serve as a stable visual regression contract.

## Included cases

* `line_sota_compare`: multi-series line plot using grayscale-safe redundant encoding
* `line_training_curve`: compact training dynamics view for method comparison
* `bar_ablation`: sorted ablation study figure
* `scatter_clusters`: clustered embedding view with categorical legend
* `hist_error_distribution`: single-variable distribution summary
* `box_distribution_compare`: grouped distribution comparison
* `heatmap_metrics`: matrix-style metric comparison with annotations
* `bar_resource_tradeoff`: compact system cost comparison
* `report_layout`: mixed table-and-chart layout with panel labels

## Refreshing gallery assets

```bash
python -c "from paperplot import render_gallery; render_gallery('docs/gallery')"
MPLCONFIGDIR=/tmp/matplotlib-paperplot python scripts/generate_visual_baselines.py
```

The first command updates the user-facing gallery images. The second updates the regression baselines only when a visual change is intentional.
