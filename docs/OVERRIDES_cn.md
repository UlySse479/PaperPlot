# PaperPlot 图表覆盖与重写指南

本文说明如何在不修改内置实现的前提下，对 PaperPlot 图表进行定制。

PaperPlot 提供两层覆盖机制：

1. 通过 `base` 做资源级覆盖
2. 通过 `override` 做单次渲染覆盖

如果你希望得到可复用的 profile、style 或 template，使用 `base`。如果你只想对某一张图做临时调整，使用 `override`。

## 覆盖优先级

PaperPlot 解析图表时的顺序是：

1. profile
2. style
3. template
4. 渲染时的 `override`

因此，`override` 的优先级最高。

## 1. 使用 `base` 做可复用覆盖

profile、style 和 template 都可以通过 `base` 继承已有资源。PaperPlot 会将子资源递归合并到基类资源之上。

### Style 覆盖示例

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

这个配置保留了内置 `default` style，只覆盖少量视觉 token。

### Template 覆盖示例

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

这个 template 复用了内置 `bar.default`，只修改模板默认值。

### Profile 覆盖示例

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

### 加载自定义资源

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

支持的资源根目录：

* `paperplot_assets/`
* `.paperplot/`
* 直接使用 `profiles/`、`styles/`、`templates/` 目录

## 2. 使用 `override` 做单次图表覆盖

当你只想对单次渲染后的最终 spec 做补丁时，使用 `override`。

PaperPlot 将这些覆盖项解释为点路径，例如：

* `axes.grid`
* `font.size`
* `lines.linewidth`
* `template.defaults.title`
* `figure.figsize`

### Python 示例

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

### YAML 配置示例

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

然后使用下面的命令渲染：

```bash
paperplot render path/to/config.yaml
```

## `size` 和 `figure.figsize` 应该怎么选

如果你想使用 profile 中定义好的命名尺寸，使用 `size`：

```python
plot(..., size="double")
```

如果你想只对某一张图指定一个明确尺寸，使用 `override={"figure.figsize": [6.4, 3.2]}`。

只修改 `figure.size_token` 并不会真正改变渲染尺寸。实际绘图时使用的是 `figure.figsize`。

## 合并规则

`base` 对映射类型做递归合并：

* 嵌套字典会继续合并
* 非字典值会直接替换基类中的值

`override` 会直接替换你提供的点路径所对应的最终值。

例如：

```python
override={
    "axes.grid": True,
    "axes": {"grid": False}
}
```

这不是推荐写法。更合适的方式是统一使用点路径：

```python
override={
    "axes.grid": True,
    "axes.grid_alpha": 0.15,
}
```

## 常见使用模式

### 维护实验室统一 style

创建一个 `base: default` 的 style 资源，只覆盖配色、线宽和网格参数。

### 维护同一类论文模板

创建一个 `base: line.default` 或 `base: bar.default` 的 template 资源，只覆盖布局或默认参数。

### 临时修补一张导出图

当你只需要对单张图做局部调整时，在 Python 或配置文件中使用 `override`。

### 控制 legend 位置

带 legend 的模板现在统一支持下面这些渲染参数：

* `legend`
* `legend_title`
* `legend_bbox_to_anchor`
* `legend_ncol`
* `extra_legends`

示例：

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

## 推荐工作流

1. 从内置 profile、style、template 开始。
2. 先用 `override` 快速试验小改动。
3. 当某些决策稳定后，再把它们沉淀成带 `base` 的可复用资源。
4. 最后使用 `paperplot validate-config` 或直接渲染示例做验证。

## 相关文档

* [CLI.md](./CLI.md)
* [COLOR_ADVISOR_cn.md](./COLOR_ADVISOR_cn.md)
* [README.md](../README.md)
* [README_cn.md](../README_cn.md)
