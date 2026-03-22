# PaperPlot Design Document v0.3

## 1. Goal

PaperPlot is a Matplotlib-based framework for producing publication-quality scientific figures with:

* paper-level consistency
* venue-aware sizing and export defaults
* template-driven plot construction
* minimal friction for existing Matplotlib users
* config- and CLI-driven workflows for reproducible figure generation

The overall goal from earlier versions is unchanged. What changed is the implementation center: the project now uses a lean registry-plus-renderer architecture with real built-in assets on disk, optional external asset loading, and validated end-to-end rendering paths.

---

## 2. Design Direction

### 2.1 Core principles

The implemented system follows these rules:

* publication-quality first
* consistency over flexibility
* minimal abstraction
* reuse over reinvention
* validation is required

### 2.2 Architecture direction

The original design direction has been simplified into a single resolved pipeline:

```text
built-in specs + external JSON/YAML assets + config files
                         ↓
                    registry layer
                         ↓
              resolver / inheritance engine
                         ↓
          Matplotlib style application + renderer
                         ↓
               file export / gallery / CLI output
```

This keeps the user-facing goals of the original document while avoiding a heavier multi-engine or plugin-first design.

Reasons for the current approach:

* built-in Python specs are easy to validate and ship
* external JSON/YAML assets give labs and projects a stable customization path
* one resolver is easier to reason about than multiple partially overlapping config systems
* chart renderers and composite templates stay extensible without a large plugin framework

---

## 3. Architecture

### 3.1 Core layers

### 1. Asset layer

Three asset types define most figure behavior:

* `profile`
* `style`
* `template`

Built-ins live as Python modules under:

* `paperplot/profiles/`
* `paperplot/styles/`
* `paperplot/templates/`

Project-local overrides and additions can also be loaded from:

* `paperplot_assets/`
* `.paperplot/`
* direct `profiles/`, `styles/`, `templates/` directories

Supported file formats:

* `.json`
* `.yaml`
* `.yml`

### 2. Registry layer

Registries store built-in and user-defined specs:

* profile registry
* style registry
* template registry
* plotter registry

This is the extension point for custom lab templates, paper presets, and external asset bundles.

### 3. Resolver layer

One resolver produces the final figure spec by applying:

```text
profile
  + style
  + template
  + size token resolution
  + figure override
```

Key rules:

* defaults are merged first
* dotted overrides are applied last
* the resolved result is deterministic and inspectable

### 4. Rendering layer

The renderer:

* loads or normalizes input data
* resolves the final spec
* prepares a safe Matplotlib environment
* applies Matplotlib `rcParams`
* dispatches to the chart-type renderer
* applies formatter and annotation helpers
* exports the figure when requested

### 5. Workflow layer

PaperPlot exposes the rendering pipeline through:

* Python API
* config-driven execution
* CLI commands
* gallery generation
* regression-oriented tests and baselines

---

## 4. Package Structure

```text
paperplot/
├── core/
│   ├── config.py      # config loading and figure spec resolution
│   ├── io.py          # CSV and in-memory data normalization
│   ├── merge.py       # deep merge and dotted override support
│   ├── mpl.py         # Matplotlib environment preparation
│   ├── renderer.py    # render pipeline and composite layout handling
│   ├── save.py        # export helpers
│   ├── serde.py       # JSON/YAML loading
│   └── style.py       # rcParams mapping and style application
├── plots/
│   ├── annotations.py
│   ├── bar.py
│   ├── box.py
│   ├── common.py
│   ├── formatting.py
│   ├── grouped_bar.py
│   ├── heatmap.py
│   ├── hist.py
│   ├── line.py
│   ├── radar.py
│   ├── scatter.py
│   └── table.py
├── profiles/
├── registry/
│   ├── api.py
│   ├── base.py
│   └── builtins.py
├── styles/
├── templates/
├── cli.py
├── gallery.py
└── __init__.py
```

The original “maybe later” folders for `profiles/`, `styles/`, and `templates/` are now part of the implemented structure, not placeholders.

---

## 5. Resolution Model

### 5.1 Inheritance rules

### Styles

Styles may inherit from a base style:

```yaml
name: academic-muted
base: default
```

### Templates

Templates may inherit from a base template:

```yaml
name: line.sota_compare
base: line.default
```

### Profiles

Profiles are implemented as stable venue presets and do not currently chain inheritance. This keeps venue defaults predictable and avoids unnecessary complexity.

### 5.2 Figure resolution

Final resolution order:

```text
profile
→ style
→ template
→ size token resolution
→ dotted override application
```

Example override:

```python
override = {
    "lines.linewidth": 2.5,
    "axes.grid": True,
}
```

---

## 6. Public API

### 6.1 Matplotlib enhancement mode

```python
from paperplot import use_style

use_style(
    profile="icml",
    visual="academic-muted",
    size="single",
)
```

This applies PaperPlot defaults to Matplotlib without forcing template usage.

### 6.2 Template mode

```python
from paperplot import plot

fig, ax, spec = plot(
    template="line.sota_compare",
    data=df,
    x="epoch",
    y="acc",
    hue="method",
    output="figures/acc.pdf",
)
```

### 6.3 Config-driven mode

```python
from paperplot import plot_from_config

fig, ax, spec = plot_from_config("examples/bar_ablation.yaml")
```

This accepts either:

* a Python mapping
* a JSON config path
* a YAML config path

### 6.4 Registry and asset APIs

```python
from paperplot import (
    autoload_project_assets,
    register_template,
)

autoload_project_assets(".")
register_template(
    "line.my_style",
    base="line.sota_compare",
    defaults={"marker": False},
)
```

### 6.5 Figure lifecycle helper

```python
from paperplot import managed_figure, plot_from_config

with managed_figure(plot_from_config("examples/bar_ablation.yaml")) as (fig, ax, spec):
    ...
```

This keeps the existing `(fig, ax, spec)` return contract while offering automatic cleanup for long-running scripts and notebooks.

---

## 7. Supported Plot Types

Primitive chart renderers currently include:

* line
* bar
* grouped bar
* scatter
* histogram
* box
* heatmap
* radar
* table

Composite layouts currently include:

* multi-panel subplots
* table-and-figure mixed layouts

Built-in templates currently include:

* `line.default`
* `line.scaling_law`
* `line.sota_compare`
* `line.training_curve`
* `scatter.default`
* `scatter.pareto_frontier`
* `bar.default`
* `bar.ablation`
* `grouped_bar.default`
* `grouped_bar.benchmark_compare`
* `ablation.study`
* `hist.default`
* `box.default`
* `box.distribution_compare`
* `heatmap.default`
* `heatmap.benchmark_matrix`
* `radar.default`
* `table.default`
* `subplots.default`
* `table_mix.default`
* `table_mix.paper_summary`

Award-inspired templates are intentionally generic rather than paper-specific replicas. They encode recurring visual structures found in recent best-paper figure sets, especially:

* scaling-law trend figures
* Pareto frontier scatter plots
* benchmark matrix heatmaps
* grouped benchmark comparisons
* table-plus-chart summary layouts

---

## 8. Data Model

Accepted inputs currently include:

* Python mappings of column name to values
* list-like row data
* CSV file paths
* pandas objects when available, via column access

This keeps the data layer simple and avoids introducing a custom dataframe abstraction.

---

## 9. Annotation and Formatting Model

The renderer includes reusable figure semantics beyond bare chart drawing:

* manual significance brackets
* declarative significance specs with:
  * `compare`
  * `pairs`
  * `within`
  * `against`
  * `exclude`
* uncertainty rendering:
  * line error bars and confidence bands
  * bar and grouped-bar error bars
  * scatter error bars
* axis formatter helpers:
  * percent
  * percent100
  * scientific
  * compact
* axis scale controls:
  * `xscale`
  * `yscale`
* panel labels
* panel captions
* figure notes
* shared axes and global legends for composite layouts

These are part of the current plotting contract and should be considered first-class functionality, not future ideas.

---

## 10. Export Model

Exports are controlled by resolved profile and figure defaults:

* `dpi`
* `bbox_inches`
* `transparent`
* output path and format inferred from filename

The save pipeline is centralized so exported figures are consistent across templates and CLI workflows.

---

## 11. CLI and Automation

The project now includes a CLI for operational workflows:

* `paperplot render`
* `paperplot gallery`
* `paperplot assets`
* `paperplot validate`
* `paperplot validate-config`
* `paperplot validate-assets`
* `paperplot list`

Global modes:

* `--json`
* `--quiet`

The CLI is part of the supported interface, not an optional add-on.

---

## 12. Validation Strategy

Validation is required for rendering and infrastructure changes.

Current validation includes:

* config inheritance tests
* override tests
* asset-loading tests
* CLI tests
* smoke rendering tests
* gallery tests
* visual regression tests against committed baselines

The design expectation is now stronger than earlier versions:

> changes that affect visual output should be validated against representative regression cases, not only by code execution.

---

## 13. Current Non-Goals

These remain out of scope for the current implementation:

* a large plugin marketplace
* GUI or web application layer
* fully automatic statistical testing or p-value computation
* dynamic layout optimization beyond the current composite templates
* automatic caption writing

---

## 14. Implementation Status

This document now reflects the implemented repository state:

* the package structure is real and on disk
* built-in profiles, styles, and templates exist as importable modules
* inheritance and dotted overrides are implemented
* config-driven plotting supports JSON and YAML
* external asset autoloading is implemented
* the CLI is implemented and tested
* the built-in gallery and visual baselines are implemented
* primitive plots, composite layouts, annotations, and formatting helpers are wired
* regression and smoke tests cover the current contract

At this stage, future work should focus on capability depth and figure semantics, not on redesigning the core architecture.
