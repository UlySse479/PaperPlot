# PaperPlot Color Advisor 使用手册

这份文档专门讲 `paper.color_advisor`。

它解决的不是“我怎么手工填几种颜色”，而是更接近论文生产流程里的三个问题：

1. 不同图类型应该自动用什么样的科研安全配色
2. `Ours`、`Baseline`、`Teacher` 这类标签怎样在整篇论文里保持同色对应
3. 分开渲染多张图时，怎样避免颜色顺序漂移

---

## 一句话理解

`paper.style` 决定基础视觉语言，`paper.color_advisor` 决定自动推荐和跨图一致性策略。

更直接一点：

* `paper.style`：像是在选一套默认视觉 token
* `paper.color_advisor`：像是在给整篇论文指定颜色分配规则

---

## 它会做什么

启用后，PaperPlot 会基于仓库里的 `scientific-color-advisor` vendored catalog 自动选择更合适的颜色方案。

当前行为包括：

* `line` / `scatter` / `grouped_bar` / `box`：
  自动选择 qualitative palette
* `heatmap`：
  自动选择 sequential 或 diverging ramp
* 有 `hue` 的图：
  把标签解析成稳定的语义颜色映射
* 小系列数折线图：
  会根据真实 `series_count` 更严格地评估前几个颜色的分离度、克制度和对比度
* 配置了持久化路径时：
  把映射写入 JSON，保证多张图分别渲染时仍然一致

---

## 最小配置

最小可用写法：

```yaml
paper:
  profile: icml
  style: academic-muted
  color_advisor:
    enabled: true

figure:
  template: line.sota_compare
  data:
    epoch: [1, 2, 3, 1, 2, 3]
    acc: [74.1, 76.8, 78.3, 71.9, 73.5, 74.8]
    method: [Ours, Ours, Ours, Baseline, Baseline, Baseline]
  x: epoch
  y: acc
  hue: method
```

这会开启自动推荐，但还没有显式告诉系统“哪些标签是最重要的”，也没有把映射落盘。

---

## 推荐配置

论文里更推荐下面这种写法：

```yaml
paper:
  profile: icml
  style: academic-muted
  color_advisor:
    enabled: true
    usage: manuscript
    tone: restrained
    priorities: [colorblind-safe, grayscale-safe, avoid-red-green]
    namespace: my-paper
    persist_path: .paperplot/paper-colors.json
    preferred_order: [Ours, Baseline, Ablation]
    bindings:
      Ours: primary
      Baseline: secondary

figure:
  template: line.sota_compare
  data:
    epoch: [1, 2, 3, 1, 2, 3]
    acc: [74.1, 76.8, 78.3, 71.9, 73.5, 74.8]
    method: [Ours, Ours, Ours, Baseline, Baseline, Baseline]
  x: epoch
  y: acc
  hue: method
```

---

## 字段解释

### `enabled`

是否启用 advisor。

```yaml
color_advisor:
  enabled: true
```

如果不启用，PaperPlot 仍然使用普通 style palette。

### `usage`

指定图要服务于什么场景。

常用值：

* `manuscript`
* `lab-meeting`
* `poster`
* `course-slides`
* `online-document`

论文里通常优先用：

```yaml
usage: manuscript
```

### `tone`

指定推荐强度和气质。

常用值：

* `restrained`
* `balanced`
* `strong`

建议：

* 论文主文图优先 `restrained`
* 补充材料或网页图可考虑 `balanced`
* 海报和演示稿才更适合 `strong`

### `priorities`

告诉 advisor 优先优化什么。

常见值：

* `colorblind-safe`
* `grayscale-safe`
* `high-contrast`
* `avoid-red-green`
* `avoid-rainbow`

论文里推荐起点：

```yaml
priorities: [colorblind-safe, grayscale-safe, avoid-red-green]
```

### `series_count`

通常不需要手工写。

如果图里有 `hue`，PaperPlot 会从实际数据里自动推断系列数量，并用它来决定应不应该更严格地约束前几个颜色。

这对下面这种情况尤其重要：

* 只有 2 条线的论文主文图
* 只有 3 个方法的 SOTA 对比图

因为这种图最怕出现：

* 前两色太接近，缩小后分不开
* 前两色虽然很远，但过于饱和，不像论文主文

如果你确实需要手动指定，也可以写：

```yaml
series_count: 2
```

但一般建议让系统自己从数据推断。

### `namespace`

给一篇论文、一个项目、或者一个实验系列定义独立命名空间。

```yaml
namespace: icml-2026-main-paper
```

不同 namespace 的颜色映射会分开管理。

### `persist_path`

把语义标签到颜色的映射落盘到 JSON。

```yaml
persist_path: .paperplot/paper-colors.json
```

如果你把图分成很多配置文件分别渲染，这个字段很重要。没有它，就只能保证单次运行内稳定，不能保证长期复现。

### `preferred_order`

控制哪些标签优先占用前几个颜色槽。

```yaml
preferred_order: [Ours, Baseline, Ablation]
```

这很适合：

* 让 `Ours` 总是拿主色
* 让 `Baseline` 总是拿次主色
* 避免因为数据顺序变化导致颜色主次颠倒

### `bindings`

显式把标签绑定到某个颜色角色。

```yaml
bindings:
  Ours: primary
  Baseline: secondary
  Teacher: color-3
```

当前支持的常见角色：

* `primary`
* `secondary`
* `tertiary`
* `quaternary`
* `quinary`
* `color-3` 这类显式索引
* 直接写 HEX，例如 `#2D5673`

如果你已经知道论文里的颜色语义，这是最稳定的写法。

---

## 不同图类型会怎样选色

### 折线图 / 散点图 / 分组柱状图 / 箱线图

这些图会走 qualitative palette。

目标是：

* 类别之间足够分离
* 避免显著红绿冲突
* 在论文缩小和灰度环境下仍保留基本可读性

### 热图

这些图会优先根据热图类型选色。

默认情况：

* 普通 heatmap 走 sequential

如果模板或 override 指向明显的 diverging cmap，例如 `RdBu`，则会切到 diverging palette。

---

## 跨整篇论文保持对应的推荐工作流

最稳妥的方式如下：

1. 给整篇论文固定一个 `namespace`
2. 配置 `persist_path`
3. 给关键方法写 `preferred_order`
4. 如果方法角色非常稳定，再加 `bindings`

示例：

```yaml
paper:
  color_advisor:
    enabled: true
    namespace: iclr-2026-main
    persist_path: .paperplot/paper-colors.json
    preferred_order: [Ours, Best Baseline, Average Baseline]
    bindings:
      Ours: primary
      Best Baseline: secondary
```

这样做之后，即使：

* 图 A 里顺序是 `Baseline, Ours`
* 图 B 里顺序是 `Ours, Baseline`
* 图 C 只有 `Ours`

颜色仍然会保持稳定。

---

## 什么时候该用 `color_advisor`，什么时候该手工 override

适合用 `paper.color_advisor`：

* 你在做整篇论文的统一配色
* 你希望系统自动挑更稳妥的 palette
* 你担心不同 config 之间颜色漂移

适合用 `figure.override.palette.colors`：

* 你只想临时手工调整一张图
* 你已经明确知道要哪几个 HEX
* 你不需要跨图一致性管理

最常见误区是：

* 用 `override.palette.colors` 去管理整篇论文

这样通常会造成：

* 不同文件各写一套颜色
* 后期统一修改困难
* `Ours` 和 `Baseline` 在不同图里互换颜色

---

## CLI 检查与导出

如果你想在不真正渲染整张图的前提下检查 advisor 结果，可以用：

```bash
paperplot color-advisor examples/icml_color_advisor.yaml
```

这会输出 JSON，包含：

* 当前 config 使用的 recommendation
* palette
* 系列标签到颜色的映射
* 推断得到的 `series_count`
* namespace
* persist_path

如果你想把结果保存出来：

```bash
paperplot color-advisor examples/icml_color_advisor.yaml --export-map artifacts/color-map.json
```

这个文件适合：

* 检查整篇论文的颜色契约
* 作为 CI 附件留档
* 给后处理脚本或文档生成工具复用

---

## Python 端使用

除了 YAML config，也可以在 Python 里直接传：

```python
from paperplot import plot

plot(
    template="line.sota_compare",
    data={
        "epoch": [1, 2, 3, 1, 2, 3],
        "acc": [74.1, 76.8, 78.3, 71.9, 73.5, 74.8],
        "method": ["Ours", "Ours", "Ours", "Baseline", "Baseline", "Baseline"],
    },
    x="epoch",
    y="acc",
    hue="method",
    profile="icml",
    visual="academic-muted",
    color_advisor={
        "enabled": True,
        "usage": "manuscript",
        "tone": "restrained",
        "namespace": "paper-demo",
        "persist_path": ".paperplot/paper-colors.json",
        "preferred_order": ["Ours", "Baseline"],
    },
)
```

---

## 常见建议

### 建议 1

论文里默认从下面这组起步：

```yaml
usage: manuscript
tone: restrained
priorities: [colorblind-safe, grayscale-safe, avoid-red-green]
```

### 建议 2

如果你已经知道“哪条线最重要”，就写 `preferred_order`。

### 建议 3

如果论文图是分多个 config 单独渲染的，一定写 `persist_path`。

### 建议 4

如果你只是在修一张图的局部表现，不要把所有工作都塞进 `color_advisor`，局部微调仍然可以用 `figure.override`。

---

## 示例文件

仓库内可直接参考：

* [examples/icml_color_advisor.yaml](/root/PaperPlot/examples/icml_color_advisor.yaml)
* [docs/CONFIG_FIELD_GUIDE_cn.md](/root/PaperPlot/docs/CONFIG_FIELD_GUIDE_cn.md)
* [docs/CLI.md](/root/PaperPlot/docs/CLI.md)
* [docs/OVERRIDES_cn.md](/root/PaperPlot/docs/OVERRIDES_cn.md)
