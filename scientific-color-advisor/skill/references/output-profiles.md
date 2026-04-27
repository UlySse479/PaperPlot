# Output Profiles

## Scientific Figure Output

The CLI returns:

- ranked recommendations
- template metadata
- HEX list
- diagnostics summary, score, and quick-fix ids
- export payloads for `matplotlib`, `plotly`, `matlab`, `css`, `json`, and `summary`

## PPT Output

For `target=ppt`, the CLI also returns `ppt_pack`:

- `title_color`
- `body_text_color`
- `accent_colors`
- `chart_palette`
- `usage_notes`

Use the PPT pack for deck scaffolding and the chart palette for in-slide figures. v1 does not edit `.pptx` files directly.
