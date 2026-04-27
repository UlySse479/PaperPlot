---
name: scientific-color-advisor
description: Recommend scientific plotting palettes and PPT color systems with a local CLI backed by a vendored Scientific-Color-Lab template snapshot. Use when Codex needs palette advice for papers, line plots, scatter plots, bar charts, heatmaps, concept figures, course slides, or PPT decks, especially when the user wants export-ready HEX lists, Matplotlib or Plotly snippets, diagnostics, or safer alternatives to rainbow and red-green-heavy palettes.
license: Apache-2.0
---

# Scientific Color Advisor

## Overview

Use the local CLI at `scripts/scientific-color-cli.mjs` to turn scientific-figure or PPT requests into normalized protocol requests, ranked palette recommendations, diagnostics, and export-ready snippets. Prefer the vendored core so the skill works immediately after installation; use `--repo` or `SCIENTIFIC_COLOR_LAB_REPO` only when the user explicitly wants to point at a local `Scientific-Color-Lab` checkout.

## Workflow

1. Classify the request as either `scientific-figure` or `ppt`.
2. If the user expresses a visual style in natural language, explicitly translate that style into concrete protocol fields before calling the CLI.
3. Normalize the request into the protocol described in [references/protocol.md](./references/protocol.md).
4. When the style is vague, do not pass the raw phrase through. Rewrite it into specific `usage`, `tone`, `background`, `priorities`, and optional `source_colors`.
5. Call the CLI with explicit flags or `--request-json`.
6. Return the best recommendation first, then include exports or PPT usage notes as needed.
7. If the user wants reproducible downstream use, include the exact CLI command you used.

## Request Mapping

- Paper figures, chart palettes, line plots, scatter plots, bars, heatmaps, and concept figures map to `target=scientific-figure`.
- Slide themes, PPT chart colors, deck accents, and presentation color systems map to `target=ppt`.
- Require a compatible `chart_type` and `palette_class`. Reject unsupported combinations instead of inventing a fallback.
- Use `tone=restrained` for manuscript-safe or editorial requests, `tone=balanced` for neutral academic defaults, and `tone=strong` for poster or presentation-forward requests.
- Translate user concerns like "avoid rainbow", "avoid red/green", "grayscale safe", and "colorblind safe" into protocol priorities.

## Style Translation

When this skill is invoked, do not leave phrases like "xxx style" as loose prose. Convert them into protocol inputs that Scientific Color Lab can actually score.

Required behavior:

- Always rewrite style language into explicit protocol fields before calling the CLI.
- Prefer `usage`, `tone`, `background`, and `priorities` as the primary translation targets.
- Use `source_colors` only when the user gives a brand/reference color or when a concrete anchor color is clearly implied.
- If the user's style request mixes visual taste and communication intent, translate both.
- If multiple mappings are plausible, choose the shortest logically consistent mapping and state the assumption in the response.
- Do not claim the lab understands an open-ended style phrase directly; the agent must perform the translation step.

### Style Phrase -> Protocol Fields

Use the following mapping defaults unless the user provides stronger constraints.

| Style phrase or intent | Protocol translation |
| --- | --- |
| `paper style`, `journal style`, `editorial style`, `Nature-like`, `clean academic` | `usage=manuscript`, `tone=restrained`, `background=light`, add `priority=colorblind-safe` if accessibility is implied |
| `conference slide style`, `talk style`, `presentation style` | `target=ppt` if the user is designing slides; otherwise keep `scientific-figure`, use `usage=course-slides`, `tone=strong`, infer `background` from the described canvas |
| `poster style`, `showcase style` | `usage=poster`, `tone=strong`, prefer `priority=high-contrast` |
| `neutral`, `balanced`, `professional`, `not too flashy` | `tone=balanced` |
| `restrained`, `minimal`, `subtle`, `clean`, `low-key` | `tone=restrained` |
| `bold`, `strong`, `vivid`, `high energy`, `eye-catching` | `tone=strong` |
| `dark theme`, `dark background`, `on black`, `night mode` | `background=dark` |
| `light theme`, `white background`, `paper background` | `background=light` |
| `high contrast`, `projector friendly`, `easy to distinguish` | add `priority=high-contrast` |
| `colorblind safe`, `accessible` | add `priority=colorblind-safe` |
| `grayscale safe`, `print safe` | add `priority=grayscale-safe` |
| `avoid red green`, `no red-green confusion` | add `priority=avoid-red-green` |
| `avoid rainbow`, `scientific heatmap`, `perceptually safer heatmap` | add `priority=avoid-rainbow` |
| `use our brand blue`, `based on this reference color`, `around #xxxxxx` | add `source_colors=[...]` with the supplied color |

### Narrative Intent -> Color Strategy

When the user is not only asking for style but also for rhetorical emphasis, translate that intent into protocol choices plus response guidance.

| Narrative intent | Translation rule |
| --- | --- |
| `show our model is best`, `highlight our method`, `突出我们的方法` | Keep the selected palette, but reserve the strongest or highest-contrast accent for the primary series and assign more muted colors to baselines. Prefer `tone=balanced` or `tone=strong` depending on context. |
| `show steady improvement`, `emphasize trend` | For line plots, prefer palettes with clear categorical spacing and good luminance separation; add `priority=high-contrast` when legibility matters. |
| `show uncertainty carefully`, `avoid overstating differences` | Prefer `tone=restrained`; avoid very saturated palettes unless the user explicitly asks for presentation-forward styling. |
| `make the key series pop on slides` | Use `usage=course-slides` or `poster` and `tone=strong`; mention that the key series should take the dominant accent while comparison lines stay quieter. |

### Agent Response Pattern

When the user gives a style phrase, the agent should internally follow this structure before calling the CLI:

1. Parse the user's chart type, medium, and communication goal.
2. Rewrite the style phrase into protocol fields.
3. Call the CLI with those fields.
4. In the final answer, briefly say how the style was translated.

Example:

- User asks: `Please design a Nature-like line chart to highlight our model advantage.`
- Translate to: `target=scientific-figure`, `chart_type=line-plot`, `palette_class=qualitative`, `usage=manuscript`, `tone=restrained`, `background=light`, `priorities=[colorblind-safe]`
- Response note: `Interpreted "Nature-like" as a manuscript-safe restrained palette, and reserved the strongest accent for your method line.`

## CLI Usage

Recommendation:

```bash
node scripts/scientific-color-cli.mjs recommend --target scientific-figure --chart-type line-plot --palette-class qualitative --usage manuscript --background light --tone restrained
```

Export:

```bash
node scripts/scientific-color-cli.mjs export --target scientific-figure --chart-type heatmap --palette-class diverging --usage poster --background dark --tone strong --format matplotlib --format css
```

Health check:

```bash
node scripts/scientific-color-cli.mjs doctor --repo C:/path/to/Scientific-Color-Lab
```

## Canonical Examples

- Manuscript line plot:
  `node scripts/scientific-color-cli.mjs recommend --target scientific-figure --chart-type line-plot --palette-class qualitative --usage manuscript --background light --tone restrained --priority colorblind-safe --priority avoid-red-green`
- Poster heatmap export:
  `node scripts/scientific-color-cli.mjs export --target scientific-figure --chart-type heatmap --palette-class sequential --usage poster --background dark --tone strong --format matplotlib --format css`
- Course-slide PPT pack:
  `node scripts/scientific-color-cli.mjs recommend --target ppt --chart-type presentation-slide --palette-class qualitative --usage course-slides --background dark --tone strong`

## Output Guidance

- Keep the response concise and practical.
- Include the recommended template name, HEX list, and the reason it fits the requested scientific or PPT context.
- If `output=json` is useful for the user's workflow, mention that the CLI supports it.
- For PPT requests, include the slide-role pack and usage notes from [references/output-profiles.md](./references/output-profiles.md).

## Local Repo Mode

- Vendored mode is the default.
- If the user explicitly mentions a local `Scientific-Color-Lab` checkout, append `--repo <path>` or set `SCIENTIFIC_COLOR_LAB_REPO`.
- Use local repo mode for doctor or drift-check tasks first; do not assume the local checkout is always available.
