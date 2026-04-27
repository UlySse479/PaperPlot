# Overriding Figures in PaperPlot

This guide explains how to customize a PaperPlot figure without forking built-in code.

PaperPlot supports two override layers:

1. Asset-level overrides with `base`
2. Render-time overrides with `override`

Use `base` when you want a reusable custom profile, style, or template. Use `override` when you want a one-off adjustment for a specific figure.

## Override Order

PaperPlot resolves a figure in this order:

1. profile
2. style
3. template
4. render-time `override`

That means render-time `override` has the highest priority.

## 1. Reusable Overrides with `base`

Profiles, styles, and templates can inherit from an existing asset by setting `base`. PaperPlot deep-merges the child asset onto the base asset.

### Style override example

`examples/assets/styles/lab-muted.json`:

```json
{
  "name": "lab-muted",
  "base": "default",
  "palette": {
    "colors": ["#1E3A5F", "#5C7A99", "#C4834A", "#8C5E58"]
  },
  "axes": {
    "grid": true,
    "grid_alpha": 0.14
  },
  "lines": {
    "linewidth": 2.15
  }
}
```

This keeps the built-in `default` style and overrides only a few visual tokens.

### Template override example

`examples/assets/templates/bar.lab.json`:

```json
{
  "name": "bar.lab",
  "base": "bar.default",
  "defaults": {
    "sort": true,
    "title": "Lab Benchmark"
  }
}
```

This reuses the built-in `bar.default` template and changes only the template defaults.

### Profile override example

`examples/assets/profiles/lab.json`:

```json
{
  "name": "lab",
  "font": {
    "family": "serif",
    "size": 9,
    "title_size": 9,
    "label_size": 9,
    "tick_size": 8,
    "mathtext_fontset": "dejavuserif"
  },
  "sizes": {
    "single": [3.05, 2.15],
    "double": [6.45, 3.0],
    "square": [3.0, 3.0]
  },
  "export": {
    "formats": ["pdf", "png"],
    "dpi": 300,
    "bbox_inches": "tight",
    "transparent": false
  }
}
```

### Loading custom assets

```python
from paperplot import autoload_project_assets, plot

autoload_project_assets("examples/assets")

plot(
    template="bar.lab",
    profile="lab",
    visual="lab-muted",
    data={"model": ["A", "B", "C"], "score": [81.2, 83.4, 82.7]},
    x="model",
    y="score",
)
```

Supported asset roots:

* `paperplot_assets/`
* `.paperplot/`
* direct `profiles/`, `styles/`, `templates/` directories

## 2. One-Off Figure Overrides with `override`

Use the `override` argument when you want to patch the resolved figure spec for a single render.

PaperPlot applies these overrides as dotted paths such as:

* `axes.grid`
* `font.size`
* `lines.linewidth`
* `template.defaults.title`
* `figure.figsize`

### Python example

```python
from paperplot import plot

data = {
    "epoch": [1, 2, 3, 1, 2, 3],
    "acc": [70, 73, 75, 68, 71, 74],
    "method": ["A", "A", "A", "B", "B", "B"],
}

plot(
    template="line.sota_compare",
    data=data,
    x="epoch",
    y="acc",
    hue="method",
    override={
        "axes.grid": True,
        "font.size": 8,
        "lines.linewidth": 2.4,
        "template.defaults.title": "Custom Training Curve",
    },
)
```

### YAML config example

```yaml
paper:
  profile: neurips
  style: academic-bright

figure:
  template: line.training_curve
  data:
    epoch: [1, 2, 3, 4]
    score: [71.2, 73.4, 74.8, 75.1]
  x: epoch
  y: score
  output: figures/training_curve.pdf
  override:
    axes.grid: true
    axes.grid_alpha: 0.2
    lines.linewidth: 2.3
    template.defaults.title: "Internal Experiment"
```

Then render it with:

```bash
paperplot render path/to/config.yaml
```

## Choosing Between `size` and `figure.figsize`

Use `size` when you want a named size from the selected profile:

```python
plot(..., size="double")
```

Use `override={"figure.figsize": [6.4, 3.2]}` when you want an explicit one-off figure size.

Changing only `figure.size_token` in `override` is not enough to resize the figure. The actual rendered size comes from `figure.figsize`.

## What Gets Merged

`base` performs a recursive merge for mappings:

* nested dictionaries are merged
* non-dictionary values replace the base value

`override` also replaces the final value at the dotted path you provide.

For example:

```python
override={
    "axes.grid": True,
    "axes": {"grid": False}
}
```

is not the intended pattern. Use dotted keys consistently instead:

```python
override={
    "axes.grid": True,
    "axes.grid_alpha": 0.15,
}
```

## Practical Patterns

### Keep a lab-specific style

Create a style asset with `base: default` and override palette, line width, and grid appearance.

### Keep a paper-family template

Create a template asset with `base: line.default` or `base: bar.default` and override only layout or defaults.

### Patch one exported figure

Use `override` in Python or in the config file when you only need a local adjustment for one figure.

### Control legend placement

Legend-bearing templates now support shared render-time controls:

* `legend`
* `legend_title`
* `legend_bbox_to_anchor`
* `legend_ncol`
* `extra_legends`

Example:

```yaml
figure:
  template: line.sota_compare
  data:
    epoch: [1, 2, 3, 1, 2, 3]
    acc: [70, 73, 75, 68, 71, 74]
    method: [A, A, A, B, B, B]
  x: epoch
  y: acc
  hue: method
  legend: upper left
  legend_title: Model
  legend_bbox_to_anchor: [0.0, 1.02]
  legend_ncol: 2
  extra_legends:
    - title: Metric
      loc: lower right
      entries:
        - label: Main
          color: "#666666"
          linestyle: "--"
        - label: Reference
          color: "#999999"
          linestyle: "-"
```

## Recommended Workflow

1. Start from a built-in profile, style, and template.
2. Use `override` to explore small changes quickly.
3. Move stable decisions into reusable assets with `base`.
4. Validate the final result with `paperplot validate-config` or by rendering examples.

## Related References

* [CLI.md](./CLI.md)
* [COLOR_ADVISOR_cn.md](./COLOR_ADVISOR_cn.md)
* [README.md](../README.md)
* [README_cn.md](../README_cn.md)
