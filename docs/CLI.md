# PaperPlot CLI

This document is the operational reference for the `paperplot` command.

## Figure Lifecycle

The CLI handles figure cleanup internally. If you use the Python API instead, treat returned Matplotlib figures as owned resources and close them explicitly in long-running processes:

```python
import matplotlib.pyplot as plt
from paperplot import plot_from_config

fig, ax, spec = plot_from_config("examples/bar_ablation.yaml")
plt.close(fig)
```

If you prefer automatic cleanup around the existing tuple return value, use `managed_figure(...)`:

```python
from paperplot import managed_figure, plot_from_config

with managed_figure(plot_from_config("examples/bar_ablation.yaml")) as (fig, ax, spec):
    print(spec["template"]["name"])
```

## Commands

### Render a single config

```bash
paperplot render examples/bar_ablation.yaml
paperplot render examples/grouped_ablation_significance.yaml
```

### Render a directory of configs

```bash
paperplot render configs/
```

Use `--glob` to narrow the matched files:

```bash
paperplot render configs/ --glob "*.yaml"
```

### Override output for a single config

```bash
paperplot render examples/bar_ablation.yaml --output figures/ablation.png
```

### Render with external assets

```bash
paperplot render configs/ \
  --project-root . \
  --assets examples/assets
```

### Render the built-in gallery

```bash
paperplot gallery docs/gallery
```

### Inspect loaded assets

```bash
paperplot assets examples/assets
paperplot assets examples/assets --direct
```

### Validate configs

```bash
paperplot validate-config examples/bar_ablation.yaml
paperplot validate-config configs/
```

### Validate assets

```bash
paperplot validate-assets examples/assets
paperplot validate-assets examples/assets --direct
```

### Inspect color-advisor output

```bash
paperplot color-advisor examples/icml_color_advisor.yaml
```

This prints a structured JSON report with:

* the chosen scientific-color-advisor recommendation
* the resolved palette
* the current semantic series-to-color mapping
* the inferred or configured `series_count`
* the namespace and persistence path, when configured

Export the report to a file:

```bash
paperplot color-advisor examples/icml_color_advisor.yaml --export-map artifacts/color-map.json
```

If the config has a `hue` field, the CLI infers `series_count` from the unique hue labels before scoring the recommendation. This matters for small manuscript figures where two-series color spacing should be judged more strictly than a five-series palette.

### List registered items

```bash
paperplot list
paperplot list templates
paperplot list plotters
```

## Output Modes

### Structured JSON

Use `--json` when the result will be consumed by scripts or CI:

```bash
paperplot --json validate-config examples/bar_ablation.yaml
paperplot --json list templates
```

Success output example:

```json
{"configs": ["examples/bar_ablation.yaml"], "templates": ["bar.ablation"]}
```

Error output example:

```json
{"error": "No config files found under missing.yaml", "type": "FileNotFoundError"}
```

### Quiet mode

Use `--quiet` when only the exit code matters:

```bash
paperplot --quiet validate-config examples/bar_ablation.yaml
```

## CI-Friendly Examples

### Fail the build if configs are invalid

```bash
paperplot --json validate-config configs/
```

### Fail the build if assets are invalid

```bash
paperplot --json validate-assets .
```

### Print available templates during CI debugging

```bash
paperplot --json list templates
```

### Inspect the palette contract for a paper figure

```bash
paperplot color-advisor examples/icml_color_advisor.yaml --export-map artifacts/color-map.json
```

### Render a smoke-test figure set

```bash
paperplot render examples/
```

## Significance Spec Examples

Simple pair comparison:

```yaml
significance:
  - compare: [A, B]
    text: "*"
```

Apply the same baseline comparison within every grouped-bar category:

```yaml
significance:
  - within: each
    against: Base
    text: p<0.05
```

Compare against a baseline across all categories while excluding one:

```yaml
significance:
  - within: all
    against: Base
    exclude: [Oracle]
    text: [ns, "**"]
```

## Backward Compatibility

The legacy command remains available:

```bash
paperplot validate <target>
```

Prefer:

* `paperplot validate-config ...`
* `paperplot validate-assets ...`

The explicit commands are easier to reason about in automation and CI.

## Related References

* [../README.md](../README.md)
* [COLOR_ADVISOR_cn.md](./COLOR_ADVISOR_cn.md)
* [OVERRIDES.md](./OVERRIDES.md)
