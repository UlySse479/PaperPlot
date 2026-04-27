# Protocol v1

All structured requests share `protocol_version: 1`.

## Request Shape

```json
{
  "protocol_version": 1,
  "target": "scientific-figure",
  "chart_type": "line-plot",
  "palette_class": "qualitative",
  "usage": "manuscript",
  "background": "light",
  "tone": "restrained",
  "series_count": 5,
  "priorities": ["colorblind-safe", "avoid-red-green"],
  "source_colors": ["#2D5673"],
  "output": "human"
}
```

## Allowed Values

- `target`: `scientific-figure` | `ppt`
- `chart_type`: `line-plot` | `scatter-plot` | `bar-chart` | `heatmap` | `concept-figure` | `presentation-slide`
- `palette_class`: `qualitative` | `sequential` | `diverging` | `cyclic` | `concept`
- `usage`: `manuscript` | `lab-meeting` | `poster` | `course-slides` | `online-document`
- `background`: `light` | `dark`
- `tone`: `restrained` | `balanced` | `strong`
- `priorities`: any subset of `colorblind-safe`, `grayscale-safe`, `high-contrast`, `avoid-red-green`, `avoid-rainbow`
- `output`: `human` | `json`

## Compatibility Rules

- `line-plot`, `scatter-plot`, and `bar-chart` require `palette_class=qualitative`
- `heatmap` requires `palette_class=sequential|diverging|cyclic`
- `concept-figure` requires `palette_class=concept`
- `presentation-slide` requires `palette_class=qualitative`

Reject unsupported combinations instead of substituting a nearby mode.

## CLI Flag Mapping

- `--chart-type` -> `chart_type`
- `--palette-class` -> `palette_class`
- `--priority` can be repeated or comma-separated
- `--source-color` can be repeated
- `--request-json` accepts the entire request object as JSON
- `--output json` switches stdout to machine-readable JSON
