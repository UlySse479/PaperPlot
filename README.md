# PaperPlot

PaperPlot is a minimal, opinionated plotting toolkit for generating **publication-quality figures** using Matplotlib.

It is designed for researchers who want:
- Consistent figure styles across papers
- Reusable plotting templates
- Clean, minimal APIs without heavy abstraction
- High-quality export (PDF / SVG / PNG) out of the box

> PaperPlot is not a general-purpose visualization library.  
> It focuses on **academic figures** only.

---

## ✨ Features

- 📐 **Publication-ready defaults**
  - Proper font sizes, line widths, spacing, and layout
- 🎨 **Design tokens system**
  - Centralized control of figure aesthetics
- 🧩 **Theme + Template layering**
  - Base styles + reusable high-level templates
- 📊 **Core plot types (v0.1)**
  - Line plot
  - Bar plot
  - Histogram
  - Box plot
- 📦 **Multiple export formats**
  - PNG / PDF / SVG
- 🔁 **Template reuse**
  - Register and reuse custom plotting styles

---

## 🚀 Quick Start

```python
import numpy as np
from paperplot import line_plot, export

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = line_plot(
    x=x,
    y=y,
    title="Sine Wave",
    xlabel="x",
    ylabel="sin(x)",
)

export(fig, "outputs/sine.pdf")
````

---

## 🧠 Core Concepts

### 1. Design Tokens

PaperPlot uses **design tokens** to define all visual properties:

* figure size
* font sizes
* line widths
* colors
* grid styles
* spacing

These tokens ensure consistency across all figures.

---

### 2. Theme

A **theme** defines a base style:

```python
theme="paper"
```

or

```python
from paperplot import Theme
theme = Theme.default()
```

---

### 3. Template

A **template** is a higher-level style built on top of tokens.

```python
template="icml"
```

Templates allow:

* consistent styling across multiple figures
* reuse of previously defined figure styles

---

### 4. Overrides

You can override any style locally:

```python
fig, ax = line_plot(
    x=x,
    y=y,
    overrides={
        "figure.width": 3.5,
        "font.size": 8,
    },
)
```

---

### 🔁 Style Priority

PaperPlot resolves styles in the following order:

```
default tokens
< theme
< template
< local overrides
```

---

## 📊 Supported Plots (v0.1)

### Line Plot

```python
from paperplot import line_plot
```

### Bar Plot

```python
from paperplot import bar_plot
```

### Histogram

```python
from paperplot import hist_plot
```

### Box Plot

```python
from paperplot import box_plot
```

---

## 🎨 Templates

Register your own template:

```python
from paperplot import register_template

register_template("my_template", {
    "font.size": 9,
    "line.width": 1.2,
})
```

Use it:

```python
line_plot(x, y, template="my_template")
```

---

## 📤 Exporting Figures

```python
from paperplot import export

export(fig, "figure.pdf")
export(fig, "figure.png")
export(fig, "figure.svg")
```

---

## 📁 Project Structure

```
paperplot/
  src/paperplot/
  examples/
  tests/
```

---

## 🧪 Examples

See the `examples/` directory:

* `line_basic.py`
* `bar_basic.py`
* `hist_basic.py`
* `box_basic.py`
* `template_demo.py`

---

## 🧭 Philosophy

PaperPlot follows a few strict principles:

* **Minimal over flexible**
* **Consistency over customization**
* **Explicit over magic**
* **Reusable over one-off styling**

---

## 🚫 What PaperPlot is NOT

* Not a replacement for Matplotlib
* Not a grammar-of-graphics system
* Not an interactive visualization tool
* Not a dashboard or web plotting library

---

## 🔜 Roadmap

### v0.1

* Core plots
* Token system
* Template system
* Export pipeline

### v0.2 (planned)

* Multi-panel figures
* Subplot layout system
* Better legend/layout control
* More built-in templates (ICML / ACL / Nature)

---

## 📄 License

MIT License