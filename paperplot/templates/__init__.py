"""Built-in plot templates."""

from paperplot.templates.ablation_study import TEMPLATE as ABLATION_STUDY_TEMPLATE
from paperplot.templates.bar_ablation import TEMPLATE as BAR_ABLATION_TEMPLATE
from paperplot.templates.bar_default import TEMPLATE as BAR_DEFAULT_TEMPLATE
from paperplot.templates.box_default import TEMPLATE as BOX_DEFAULT_TEMPLATE
from paperplot.templates.box_distribution_compare import (
    TEMPLATE as BOX_DISTRIBUTION_COMPARE_TEMPLATE,
)
from paperplot.templates.grouped_bar_default import TEMPLATE as GROUPED_BAR_DEFAULT_TEMPLATE
from paperplot.templates.grouped_bar_benchmark_compare import TEMPLATE as GROUPED_BAR_BENCHMARK_COMPARE_TEMPLATE
from paperplot.templates.heatmap_benchmark_matrix import TEMPLATE as HEATMAP_BENCHMARK_MATRIX_TEMPLATE
from paperplot.templates.heatmap_default import TEMPLATE as HEATMAP_DEFAULT_TEMPLATE
from paperplot.templates.hist_default import TEMPLATE as HIST_DEFAULT_TEMPLATE
from paperplot.templates.line_default import TEMPLATE as LINE_DEFAULT_TEMPLATE
from paperplot.templates.line_scaling_law import TEMPLATE as LINE_SCALING_LAW_TEMPLATE
from paperplot.templates.line_sota_compare import TEMPLATE as LINE_SOTA_COMPARE_TEMPLATE
from paperplot.templates.line_training_curve import TEMPLATE as LINE_TRAINING_CURVE_TEMPLATE
from paperplot.templates.radar_default import TEMPLATE as RADAR_DEFAULT_TEMPLATE
from paperplot.templates.scatter_default import TEMPLATE as SCATTER_DEFAULT_TEMPLATE
from paperplot.templates.scatter_pareto_frontier import TEMPLATE as SCATTER_PARETO_FRONTIER_TEMPLATE
from paperplot.templates.subplots_default import TEMPLATE as SUBPLOTS_DEFAULT_TEMPLATE
from paperplot.templates.table_default import TEMPLATE as TABLE_DEFAULT_TEMPLATE
from paperplot.templates.table_mix_default import TEMPLATE as TABLE_MIX_DEFAULT_TEMPLATE
from paperplot.templates.table_mix_paper_summary import TEMPLATE as TABLE_MIX_PAPER_SUMMARY_TEMPLATE


TEMPLATES = {
    "line.default": LINE_DEFAULT_TEMPLATE,
    "line.scaling_law": LINE_SCALING_LAW_TEMPLATE,
    "line.sota_compare": LINE_SOTA_COMPARE_TEMPLATE,
    "line.training_curve": LINE_TRAINING_CURVE_TEMPLATE,
    "scatter.default": SCATTER_DEFAULT_TEMPLATE,
    "scatter.pareto_frontier": SCATTER_PARETO_FRONTIER_TEMPLATE,
    "bar.default": BAR_DEFAULT_TEMPLATE,
    "bar.ablation": BAR_ABLATION_TEMPLATE,
    "grouped_bar.default": GROUPED_BAR_DEFAULT_TEMPLATE,
    "grouped_bar.benchmark_compare": GROUPED_BAR_BENCHMARK_COMPARE_TEMPLATE,
    "hist.default": HIST_DEFAULT_TEMPLATE,
    "box.default": BOX_DEFAULT_TEMPLATE,
    "box.distribution_compare": BOX_DISTRIBUTION_COMPARE_TEMPLATE,
    "heatmap.default": HEATMAP_DEFAULT_TEMPLATE,
    "heatmap.benchmark_matrix": HEATMAP_BENCHMARK_MATRIX_TEMPLATE,
    "radar.default": RADAR_DEFAULT_TEMPLATE,
    "table.default": TABLE_DEFAULT_TEMPLATE,
    "ablation.study": ABLATION_STUDY_TEMPLATE,
    "subplots.default": SUBPLOTS_DEFAULT_TEMPLATE,
    "table_mix.default": TABLE_MIX_DEFAULT_TEMPLATE,
    "table_mix.paper_summary": TABLE_MIX_PAPER_SUMMARY_TEMPLATE,
}

__all__ = ["TEMPLATES"]
