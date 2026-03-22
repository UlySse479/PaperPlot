---
name: plot-regression-playbook
description: Use this skill when verifying that figure outputs remain stable over time. Trigger when modifying rendering logic, styles, layouts, or any code that may affect visual output. Especially important when changes are “small” or “internal” but may cause subtle visual drift.
---

# Purpose

This skill defines how to **detect, reason about, and handle visual regressions** in PaperPlot.

It is NOT about:
- writing generic tests
- checking if code runs

It IS about:
- preventing silent visual drift
- catching subtle layout/style changes
- ensuring figures remain stable across iterations

---

# When to use

Use this skill when:

- modifying rendering code
- changing themes / tokens / defaults
- updating layout logic
- refactoring plotting internals
- introducing new plot types
- something “should not change output”

Especially use when:
> “This change shouldn’t affect visuals”

That is when regressions usually happen.

---

# Core principle (non-obvious)

Most visual regressions are **not obvious differences**.

They are:
- 2px shifts
- slightly lighter colors
- tighter spacing
- font scaling inconsistencies

These accumulate → and degrade perceived quality.

---

# Mental model

You are not checking:

> “Is this figure correct?”

You are checking:

> “Is this figure IDENTICAL in all meaningful ways?”

If not identical → you must explain why.

---

# What counts as a regression

A regression is ANY unintended change in:

- layout
- spacing
- alignment
- color
- line width
- font size
- tick behavior
- legend behavior
- rendering order (z-order)

Even if:
- it “looks fine”
- or “arguably better”

If it is not intentional → it is a regression.

---

# Baseline philosophy

Baselines are:

- **ground truth visual contracts**
- not suggestions
- not approximations

Rule:
> If baseline changes, something must justify it.

---

# Workflow

## Step 1 — Identify scope

What could this change affect?

- specific plot type?
- all plots?
- layout system?
- styling system?

Never assume “local change”.

---

## Step 2 — Select baselines

Use:

- minimal representative plots
- not complex demos

Bad baseline:
- overloaded example

Good baseline:
- simple line plot
- simple bar plot
- edge-case layout

---

## Step 3 — Compare outputs

Compare:

- previous output (baseline)
- new output

Focus on:

- alignment
- spacing
- relative proportions
- contrast

---

## Step 4 — Classify difference

Every difference must be classified as:

1. **No difference**
2. **Acceptable change (intentional)**
3. **Regression (unintended)**

You must not skip classification.

---

## Step 5 — Justify or reject

If change exists:

- explain cause
- explain impact
- decide:
  - accept (and update baseline)
  - reject (fix code)

---

# What to compare (non-obvious)

Do NOT focus only on pixels.

Focus on:

## 1. Relative geometry

- spacing between elements
- alignment consistency
- margins

---

## 2. Visual weight

- thickness of lines
- dominance of elements

---

## 3. Hierarchy

- what draws attention first?
- did that change?

---

## 4. Readability at scale

- imagine downscaling
- does anything break?

---

## 5. Consistency across plots

- same theme → same behavior?

---

# Gotchas (common LLM failures)

## Gotcha 1: “Looks the same”

LLM tends to ignore:

- small spacing shifts
- font differences

Fix:
- compare structure, not impression

---

## Gotcha 2: Silent baseline update

LLM often:

> “Update baseline since output changed”

This is WRONG unless justified.

---

## Gotcha 3: Accepting improvements without reasoning

Even if change looks better:

- it must be explained
- it must be intentional
- it must not break consistency elsewhere

---

## Gotcha 4: Testing only one example

Regression may not appear in:

- simple cases

Always consider:
- edge layouts
- multiple plot types

---

## Gotcha 5: Ignoring cross-plot consistency

A fix in one plot may:

- break another

---

## Gotcha 6: Overfitting to pixel match

Exact pixel diff is not always the goal.

Focus on:
- structural equivalence
- visual intent

---

## Gotcha 7: Forgetting determinism

If output changes between runs:

- regression detection becomes meaningless

---

# Acceptable changes (strict rules)

A change is acceptable ONLY if:

- it is intentional
- it improves:
  - readability OR
  - consistency OR
  - correctness
- it does not introduce inconsistency elsewhere

If accepted:

- document why
- update baseline explicitly

---

# Unacceptable changes

Always reject if:

- unexplained
- inconsistent across plots
- reduces readability
- introduces layout instability
- breaks theme consistency

---

# File system & organization

Treat regression as a system, not ad hoc checks.

## Recommended structure

```text
tests/
  regression/
    line/
      baseline.png
    bar/
      baseline.png
    hist/
      baseline.png
    box/
      baseline.png