# 📊 PaperPlot

> A Matplotlib-based framework for **consistent, publication-quality scientific figures**.

PaperPlot helps you move from *manual plotting and ad-hoc styling* to a **standardized, template-driven workflow** for academic papers.

---

## ✨ Why PaperPlot?

If you’ve ever struggled with:

* Inconsistent fonts and styles across figures
* Rewriting plotting scripts for every paper
* Adjusting figure sizes for different venues (ICML, ACL, CVPR…)
* Ugly default Matplotlib plots
* Hard-to-reuse complex figures (ablation, comparisons, etc.)

PaperPlot is designed for you.

---

## 🚀 Key Features

### 🎯 Paper-level Consistency

* Unified fonts, sizes, colors, and layout across all figures
* One configuration → consistent entire paper

### 🏛️ Venue-aware Profiles

Built-in support for:

* ICML / NeurIPS
* ACL / EMNLP / NAACL
* CVPR
* Nature-style figures

---

### 🎨 Hierarchical Style System

```text
Profile (venue)
   ↓
Visual Style
   ↓
Override
   ↓
Template
```

* Clean defaults
* Flexible overrides
* No more style chaos

---

### 🧩 Template-driven Plotting

Stop rewriting plotting code.

```python
from paperplot import plot

plot(
    template="line.sota_compare",
    data=df,
    x="epoch",
    y="accuracy",
    hue="method",
    output="figures/acc.pdf"
)
```

---

### 🔁 Reusable Templates

* Register your own plotting templates
* Reuse across projects and papers

```python
register_template(
    name="line.my_lab_style",
    base="line.sota_compare"
)
```

---

### 🔧 Minimal Migration Cost

Already using Matplotlib? No problem.

```python
from paperplot import use_style

use_style(profile="icml", visual="academic-muted")

plt.plot(x, y)
plt.savefig("fig.pdf")
```

---

### 📦 Multiple Input Formats

Supports:

* CSV
* pandas DataFrame
* numpy arrays
* Python dict/list

---

### 📐 Size Tokens (Paper-friendly)

Instead of manually tuning figsize:

```python
size="single"   # single column
size="double"   # double column
size="square"
```

---

### 📤 Publication-ready Export

Automatically handles:

* PDF / PNG / SVG
* DPI
* tight layout
* font embedding

---

## 📚 Quick Start

### Installation (coming soon)

```bash
pip install paperplot
```

---

### Example: Line Plot

```python
from paperplot import plot
import pandas as pd

df = pd.read_csv("results.csv")

plot(
    template="line.sota_compare",
    data=df,
    x="epoch",
    y="accuracy",
    hue="method",
    output="figures/acc.pdf"
)
```

---

### Example: Use with Existing Matplotlib Code

```python
from paperplot import use_style
import matplotlib.pyplot as plt

use_style(profile="icml", visual="academic-muted")

plt.plot(x, y)
plt.xlabel("Epoch")
plt.ylabel("Accuracy (%)")
plt.savefig("fig.pdf")
```

---

## ⚙️ Configuration (YAML)

PaperPlot supports config-driven workflows:

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

## 🧠 Design Philosophy

PaperPlot is built on one core idea:

> **Scientific plotting should be standardized, not handcrafted.**

Instead of:

* tweaking styles manually
* duplicating plotting scripts
* fighting Matplotlib defaults

You get:

* reusable templates
* consistent styles
* venue-aware figures

---

## 🏗️ Project Structure

```text
paperplot/
├── profiles/        # venue configs (ICML, ACL, etc.)
├── styles/          # visual styles
├── templates/       # reusable plot templates
├── plots/           # plot implementations
├── core/            # config + rendering engine
├── registry/        # template/style registry
└── tests/
```

---

## 📊 Supported Plots (v0.1)

* ✅ Line plot
* ✅ Bar plot
* ✅ Histogram
* ✅ Box plot

More coming soon:

* Heatmaps
* Scatter plots
* Multi-panel figures
* Ablation templates

---

## 🛣️ Roadmap

### v0.1 (MVP)

* Style system
* Template system
* Core plots (line, bar, hist, box)

### v0.2

* More templates
* Advanced layouts
* CLI support

### v0.3

* Smart layout
* Style inference
* Figure composition tools

---

## 🤝 Contributing

Contributions are welcome!

* Add new templates
* Improve styles
* Support new plot types
* Improve documentation

---

## 📄 License

MIT License

---

## ⭐ Final Note

PaperPlot is not just another plotting wrapper.

> It’s a step toward making **scientific visualization reproducible, consistent, and efficient**.

