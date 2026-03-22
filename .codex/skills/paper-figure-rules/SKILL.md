---
name: paper-figure-rules
description: Use this skill when evaluating, refining, or implementing figures intended for academic papers (e.g., ICML, ICLR, ACL, Nature). Trigger when visual quality, readability, or publication standards matter — especially when a plot “looks fine” but may fail under real paper constraints (small size, grayscale, reviewer scrutiny).
---

# Purpose

This skill encodes **non-obvious heuristics for academic figures**.

It is NOT about:
- basic matplotlib usage
- generic “make it pretty” advice

It IS about:
- catching subtle quality failures
- avoiding reviewer-visible mistakes
- making figures survive real paper conditions

---

# When to use

Use this skill when:

- a figure is being implemented or refined
- a plot will appear in a paper (conference/journal)
- something “looks okay” but might degrade in print
- reviewing output from `rendering-agent`
- validating before final export

Do NOT use this skill for:
- raw plotting implementation
- system design
- basic visualization tutorials

---

# Core principle (non-obvious)

A figure is **not evaluated at the size you see it on screen**.

It is evaluated at:
- ~50%–70% downscale
- grayscale
- low attention from a reviewer

If it fails there, it fails.

---

# Mental model

Always think in this order:

1. Can this be understood in 2 seconds?
2. Can this be read when shrunk?
3. Can this be distinguished without color?
4. Can this survive being printed?
5. Can this be understood without the caption?

If any answer is "no" → the figure is not ready.

---

# High-impact rules (non-obvious only)

## 1. Contrast beats color

Bad:
- relying on different hues with similar luminance

Good:
- differences in:
  - brightness
  - line style
  - marker shape

Rule:
> If two curves become indistinguishable in grayscale → redesign.

---

## 2. Legends are failure indicators

A large or complex legend usually means:

- too many elements
- poor encoding choices

Prefer:
- direct labeling
- fewer categories
- structural separation

---

## 3. Thin lines are invisible in papers

What looks “clean” on screen becomes:

- faint
- broken
- unreadable

Rule:
> If a line looks elegant, it's probably too thin.

---

## 4. Default matplotlib spacing is wrong

Matplotlib defaults are optimized for:

- exploration
- not publication

Common failures:
- cramped labels
- uneven margins
- misaligned titles

---

## 5. Over-precision is noise

Bad:
- too many ticks
- long decimal labels
- dense gridlines

Rule:
> Every visual element must justify its existence.

---

## 6. Color is optional, structure is mandatory

If color is removed:

- does the figure still work?

If not:
- encoding is wrong

---

## 7. Symmetry is a signal

Humans expect:

- aligned axes
- consistent spacing
- balanced layout

Small misalignments:
- reduce perceived quality immediately

---

# Gotchas (common LLM failure modes)

## Gotcha 1: “Looks good on my screen”

LLM often evaluates at full resolution.

Fix:
- mentally downscale by half
- imagine printed PDF

---

## Gotcha 2: Color-only encoding

LLM tends to:

- pick distinct colors
- ignore grayscale collapse

Fix:
- enforce redundancy (style + marker + color)

---

## Gotcha 3: Trusting matplotlib defaults

Defaults often cause:

- tiny fonts
- bad padding
- weak contrast

Fix:
- override intentionally

---

## Gotcha 4: Overcrowded plots

LLM often tries to “show everything”.

Result:
- unreadable figure
- reviewer frustration

Fix:
- split into multiple plots
- reduce categories

---

## Gotcha 5: Legend explosion

LLM frequently:

- adds legend for everything

Fix:
- ask: can I remove the legend entirely?

---

## Gotcha 6: Gridline abuse

Too many gridlines:

- add noise
- reduce clarity

Fix:
- minimal or subtle grid

---

## Gotcha 7: Font scaling mismatch

Common issue:

- axes readable
- legend unreadable

Fix:
- scale ALL text consistently

---

# Quick evaluation checklist

Use this before approving a figure:

- [ ] readable when shrunk
- [ ] distinguishable in grayscale
- [ ] no unnecessary elements
- [ ] consistent spacing
- [ ] legend minimal or unnecessary
- [ ] line widths sufficient
- [ ] labels clear and concise

---

# Progressive refinement strategy

When improving a figure:

1. Fix readability (font, size, spacing)
2. Fix distinguishability (contrast, style)
3. Remove noise (ticks, grid, legend)
4. Improve structure (layout, alignment)
5. Only then adjust aesthetics

Never start from aesthetics.

---

# Interaction guidance

When used with `rendering-agent`:

- do NOT rewrite code directly
- point out:
  - what is wrong
  - why it fails in paper context
  - what direction to fix

When used with `quality-agent`:

- provide pass/fail with justification
- highlight non-obvious risks

---

# Memory (project-specific)

If repeated issues are observed (e.g., always thin lines, always crowded legends):

- treat them as recurring failure patterns
- bias future evaluations to check them first

---

# Final rule

A figure is successful when:

- it communicates instantly,
- survives degradation,
- and does not require explanation.

If it needs explanation, it is not done.