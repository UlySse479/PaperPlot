# 📊 PaperPlot — Project Design Document v0.1

## 1. Overview

### 1.1 Project Positioning

**PaperPlot** is a Matplotlib-based scientific plotting framework designed to address common issues in academic figure creation:

* Inconsistent styles across figures (fonts, sizes, colors)
* Repeated manual tuning for different venues (ICML, ACL, CVPR, etc.)
* Low plotting efficiency (rewriting scripts for every figure)
* Poor reusability of complex plots (e.g., ablation studies, comparisons)
* Lack of *paper-level consistency* across all figures

---

### 1.2 Core Goals

PaperPlot aims to provide:

1. **Paper-level style consistency**
2. **Venue-aware plotting profiles** (ICML, NeurIPS, ACL, CVPR, Nature, etc.)
3. **Template-driven plotting** (data → figure with minimal code)
4. **Hierarchical style inheritance and override system**
5. **Reusable template registration mechanism**
6. **Minimal-intrusion compatibility with Matplotlib**

---

### 1.3 Non-Goals (v1)

* GUI tools
* Web-based visualization systems
* Automatic style extraction from images
* Replacing Matplotlib (this is a layer on top)

---

## 2. Core Design Principles

### 2.1 Hierarchical Inheritance (MOST IMPORTANT)

All configurations follow:

> **Default → Inherit → Override → Traceable**

Hierarchy:

```text
Profile (venue)
   ↓
Visual Style
   ↓
Style Override
   ↓
Template
   ↓
Figure-level override
```

---

### 2.2 Consistency First, Flexibility Second

* Defaults must ensure paper-level consistency
* Overrides are allowed, but should not break structure

---

### 2.3 Minimal Intrusion

Two supported modes:

* ✅ Enhance existing Matplotlib code (migration-friendly)
* ✅ Template-driven plotting (recommended for new projects)

---

### 2.4 Config + API Hybrid

* Python API → flexible
* YAML config → reusable and shareable

---

## 3. System Architecture

## 3.1 Four Core Layers

### 1️⃣ Profile (Venue Layer)

Defines publication constraints:

```yaml
name: icml
font_family: serif
font_scale: 1.0

sizes:
  single: [3.25, 2.2]
  double: [6.8, 3.0]
  square: [3.0, 3.0]

export:
  formats: [pdf, png]
  dpi: 300
```

---

### 2️⃣ Visual Style Layer

Defines visual aesthetics:

```yaml
name: academic-muted
base: default

palette:
  colors: ["#4C78A8", "#F58518", "#54A24B"]

axes:
  grid: true
  grid_alpha: 0.2

legend:
  frameon: false

lines:
  linewidth: 2.0
```

---

### 3️⃣ Style Override Layer

Fine-grained customization:

```python
override = {
    "lines.linewidth": 2.4,
    "axes.grid_alpha": 0.15
}
```

---

### 4️⃣ Template Layer

Defines plotting structure:

```yaml
name: line.sota_compare
chart_type: line

defaults:
  legend_loc: best
  marker: true

layout:
  size_token: single

mappings:
  required: [x, y]
  optional: [hue]
```

---

## 4. Core Modules

### 4.1 Directory Structure

```text
paperplot/
├── profiles/        # venue configs
├── styles/          # visual styles
├── templates/       # plot templates
│   ├── line/
│   ├── bar/
│   ├── hist/
│   └── box/
├── core/
│   ├── config.py
│   ├── inheritance.py
│   ├── renderer.py
│   └── save.py
├── plots/           # plot implementations
├── registry/        # registries
├── io/              # data loading
├── utils/           # helpers
└── tests/
```

---

### 4.2 Core Components

#### Config Engine

Responsible for:

* YAML parsing
* Merging profile/style/template
* Producing final config

---

#### Style Engine

Responsible for:

* Translating to Matplotlib `rcParams`
* Managing fonts, palettes, legends

---

#### Renderer

Responsible for:

* Calling plot functions
* Applying template logic

---

#### Template Registry

Supports:

* Registering templates
* Overriding templates
* Loading user-defined templates

---

## 5. API Design

### 5.1 Mode A — Enhance Matplotlib (Migration-Friendly)

```python
from paperplot import use_style

use_style(
    profile="icml",
    visual="academic-muted",
    size="single"
)

plt.plot(x, y)
plt.savefig("fig.pdf")
```

---

### 5.2 Mode B — Template-Driven Plotting (Recommended)

```python
from paperplot import plot

plot(
    template="line.sota_compare",
    data=df,
    x="epoch",
    y="acc",
    hue="method",
    output="figures/acc.pdf"
)
```

---

### 5.3 Advanced Overrides

```python
plot(
    template="line.sota_compare",
    override={
        "lines.linewidth": 2.5,
        "legend.loc": "lower right"
    }
)
```

---

### 5.4 Register Template

```python
from paperplot import register_template

register_template(
    name="line.my_style",
    base="line.sota_compare",
    defaults={
        "marker": False
    }
)
```

---

### 5.5 YAML-Driven Mode

```yaml
paper:
  profile: icml
  style: academic-muted

figure:
  template: line.sota_compare
  data: results.csv
  x: epoch
  y: acc
  hue: method
```

---

## 6. Plot Types (V1)

### Priority Plots

#### 6.1 Line Plot

* Multi-method comparison
* Marker support
* Auto legend

#### 6.2 Bar Plot

* Single variable
* Sorting support

#### 6.3 Histogram

* Auto bins
* Density support

#### 6.4 Box Plot

* Patch styling
* Outlier control

---

## 7. Style System Details

### 7.1 Font System

Unified control of:

* `font.family`
* serif / sans-serif fallback
* `mathtext.fontset`

Goals:

* Works on Linux (headless)
* Consistent PDF output

---

### 7.2 Size Token System

```python
size="single"
size="double"
size="square"
```

Mapped internally to:

```python
figsize=(3.25, 2.2)
```

---

### 7.3 Color System

Supports:

* categorical palettes
* sequential palettes
* colorblind-safe palettes

---

## 8. Template System

### 8.1 Template Levels

#### Level 1 — Parameter Templates

Simple presets

#### Level 2 — Structural Templates

Define data mappings

#### Level 3 — Logical Templates (V2)

Dynamic behavior (e.g., adaptive layout)

---

### 8.2 User Templates

```text
project/
├── templates/
│   └── my_plot.yaml
```

Auto-loaded at runtime

---

## 9. Export System

Unified interface:

```python
savefig(path)
```

Handles:

* PDF / PNG / SVG
* DPI
* bbox_inches
* layout tightening

---

## 10. MVP Scope

### Must-Have

* Profile + Style system
* YAML config
* 4 core plot types
* Template registry
* Size tokens
* Export system

---

### Not in V1

* Smart layout optimization
* Caption generation
* Style reverse engineering

---

## 11. Development Roadmap

### Phase 1 — Core Infrastructure

* Config system
* Style inheritance
* rcParams mapping

### Phase 2 — Core Plots

* Line / Bar / Histogram / Box

### Phase 3 — Template System

* Registration
* YAML support
* Examples

### Phase 4 — Enhancements

* More plot types
* CLI
* Gallery

---

## 12. Target User Experience

Ideal usage:

```python
plot(
    template="bar.ablation",
    data="ablation.csv",
    x="method",
    y="score",
    paper="icml_2026"
)
```

Produces:

* ICML-compliant figure
* Consistent fonts
* Clean color palette
* Proper sizing
* Ready for submission

---

## 13. Project Value

PaperPlot is not just about plotting.

> It transforms scientific visualization from **manual tweaking** into a **standardized, template-driven workflow**.

---

## 14. Recommended Next Step

To avoid staying at the design level:

👉 Next step should be implementation:

1. Initialize project skeleton
2. Implement `use_style()`
3. Implement `lineplot()`
4. Create ICML + Nature demo
